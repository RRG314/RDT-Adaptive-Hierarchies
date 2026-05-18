from __future__ import annotations

import hashlib
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Tuple

import numpy as np

from ..core.hierarchy import RDTHierarchy, load_imbalance, locality_dispersion, movement_fraction


def stable_key_from_index(i: int) -> int:
    digest = hashlib.blake2b(str(int(i)).encode("ascii"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def jump_consistent_hash(key: int, buckets: int) -> int:
    if buckets < 1:
        raise ValueError("buckets must be >= 1")
    key = int(key) & 0xFFFFFFFFFFFFFFFF
    b = -1
    j = 0
    while j < buckets:
        b = j
        key = (key * 2862933555777941757 + 1) & 0xFFFFFFFFFFFFFFFF
        j = int((b + 1) * (1 << 31) / ((key >> 33) + 1))
    return int(b)


def rendezvous_hash(key: int, buckets: int) -> int:
    best_bucket = 0
    best_score = -1
    key_bytes = int(key).to_bytes(8, "little", signed=False)
    for bucket in range(buckets):
        digest = hashlib.blake2b(key_bytes + bucket.to_bytes(4, "little"), digest_size=8).digest()
        score = int.from_bytes(digest, "little", signed=False)
        if score > best_score:
            best_score = score
            best_bucket = bucket
    return best_bucket


def modulo_hash(key: int, buckets: int) -> int:
    return int(key) % int(buckets)


def grid_partition(points: np.ndarray, buckets: int) -> np.ndarray:
    x = np.asarray(points, dtype=float)
    cols = int(np.ceil(np.sqrt(buckets)))
    rows = int(np.ceil(buckets / cols))
    mins = np.min(x, axis=0)
    span = np.maximum(np.ptp(x, axis=0), 1e-12)
    norm = np.clip((x - mins) / span, 0, 0.999999)
    cx = np.floor(norm[:, 0] * cols).astype(int)
    cy = np.floor(norm[:, 1 if x.shape[1] > 1 else 0] * rows).astype(int)
    raw = cy * cols + cx
    return np.minimum(raw, buckets - 1).astype(np.int64)


def _part1by1(n: np.ndarray) -> np.ndarray:
    x = n.astype(np.uint64) & np.uint64(0x0000FFFF)
    x = (x | (x << np.uint64(8))) & np.uint64(0x00FF00FF)
    x = (x | (x << np.uint64(4))) & np.uint64(0x0F0F0F0F)
    x = (x | (x << np.uint64(2))) & np.uint64(0x33333333)
    x = (x | (x << np.uint64(1))) & np.uint64(0x55555555)
    return x


def morton_codes(points: np.ndarray) -> np.ndarray:
    x = np.asarray(points, dtype=float)
    mins = np.min(x, axis=0)
    span = np.maximum(np.ptp(x, axis=0), 1e-12)
    norm = np.clip((x[:, :2] - mins[:2]) / span[:2], 0, 0.999999)
    quant = np.floor(norm * 65535).astype(np.uint64)
    return _part1by1(quant[:, 0]) | (_part1by1(quant[:, 1]) << np.uint64(1))


def morton_sort_partition(points: np.ndarray, buckets: int) -> np.ndarray:
    """Strong locality/load baseline: contiguous chunks along Morton order."""

    codes = morton_codes(points)
    order = np.argsort(codes, kind="mergesort")
    labels = np.empty(len(order), dtype=np.int64)
    ranks = np.empty(len(order), dtype=np.int64)
    ranks[order] = np.arange(len(order))
    labels = np.floor(ranks * buckets / max(1, len(order))).astype(np.int64)
    return np.minimum(labels, buckets - 1)


def principal_sort_partition(points: np.ndarray, buckets: int) -> np.ndarray:
    """Locality baseline using first principal direction and equal-size chunks."""

    x = np.asarray(points, dtype=float)
    centered = x - np.mean(x, axis=0)
    if x.shape[0] < 2:
        return np.zeros(x.shape[0], dtype=np.int64)
    _, _, vt = np.linalg.svd(centered[:, :2], full_matrices=False)
    scores = centered[:, :2] @ vt[0]
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(order), dtype=np.int64)
    ranks[order] = np.arange(len(order))
    labels = np.floor(ranks * buckets / max(1, len(order))).astype(np.int64)
    return np.minimum(labels, buckets - 1)


@dataclass
class PartitionBenchmarkResult:
    method: str
    dataset: str
    n: int
    k1: int
    k2: int
    movement: float
    imbalance_k2: float
    locality_k2: float
    build_seconds: float
    assign_seconds: float


class RDTStablePartition:
    """Stable, locality-preserving recursive partitioner.

    Existing bucket labels are preserved when a bucket splits: the left child
    keeps the parent label and the right child receives a new label. This is the
    mechanism that creates low movement during gradual resize.
    """

    def __init__(self, max_buckets: int = 128, min_leaf_size: int = 8, max_depth: int = 32):
        self.max_buckets = int(max_buckets)
        self.hierarchy = RDTHierarchy(max_leaves=max_buckets, min_leaf_size=min_leaf_size, max_depth=max_depth)

    def fit(self, points: np.ndarray) -> "RDTStablePartition":
        self.hierarchy.fit(points)
        return self

    def assign(self, points: np.ndarray, buckets: int) -> np.ndarray:
        return self.hierarchy.assign(points, buckets)

    def assign_training(self, buckets: int) -> np.ndarray:
        return self.hierarchy.labels_for_training_points(buckets)

    def movement(self, k1: int, k2: int) -> float:
        return movement_fraction(self.assign_training(k1), self.assign_training(k2))

    def resize(self, buckets: int) -> np.ndarray:
        return self.assign_training(buckets)

    def movement_to(self, labels: np.ndarray, buckets: int) -> float:
        return movement_fraction(self.assign_training(buckets), labels)

    def load_balance_score(self, buckets: int) -> float:
        return load_imbalance(self.assign_training(buckets))

    def locality_score(self, points: np.ndarray, buckets: int) -> float:
        return locality_dispersion(np.asarray(points, dtype=float), self.assign(points, buckets))


def benchmark_partition_methods(points: np.ndarray, dataset: str, k1: int = 16, k2: int = 20) -> Dict[str, PartitionBenchmarkResult]:
    x = np.asarray(points, dtype=float)
    keys = np.array([stable_key_from_index(i) for i in range(x.shape[0])], dtype=object)
    results: Dict[str, PartitionBenchmarkResult] = {}

    start = perf_counter()
    rdt = RDTStablePartition(max_buckets=max(k2, 64), min_leaf_size=8).fit(x)
    build = perf_counter() - start
    start = perf_counter()
    labels1 = rdt.assign_training(k1)
    labels2 = rdt.assign_training(k2)
    assign = perf_counter() - start
    results["rdt_stable"] = PartitionBenchmarkResult(
        "rdt_stable", dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
        load_imbalance(labels2), locality_dispersion(x, labels2), build, assign,
    )

    for name, func in {
        "modulo_hash": modulo_hash,
        "jump_hash": jump_consistent_hash,
        "rendezvous_hash": rendezvous_hash,
    }.items():
        start = perf_counter()
        labels1 = np.array([func(k, k1) for k in keys], dtype=np.int64)
        labels2 = np.array([func(k, k2) for k in keys], dtype=np.int64)
        assign = perf_counter() - start
        results[name] = PartitionBenchmarkResult(
            name, dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
            load_imbalance(labels2), locality_dispersion(x, labels2), 0.0, assign,
        )

    start = perf_counter()
    labels1 = grid_partition(x, k1)
    labels2 = grid_partition(x, k2)
    assign = perf_counter() - start
    results["grid"] = PartitionBenchmarkResult(
        "grid", dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
        load_imbalance(labels2), locality_dispersion(x, labels2), 0.0, assign,
    )

    for name, func in {
        "morton_sort": morton_sort_partition,
        "principal_sort": principal_sort_partition,
    }.items():
        start = perf_counter()
        labels1 = func(x, k1)
        labels2 = func(x, k2)
        assign = perf_counter() - start
        results[name] = PartitionBenchmarkResult(
            name, dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
            load_imbalance(labels2), locality_dispersion(x, labels2), 0.0, assign,
        )
    return results
