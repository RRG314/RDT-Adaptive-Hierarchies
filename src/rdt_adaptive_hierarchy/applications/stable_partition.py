from __future__ import annotations

import hashlib
import bisect
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Iterable, Tuple

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


def virtual_node_consistent_hash_labels(keys: Iterable[int], buckets: int, virtual_nodes: int = 64) -> np.ndarray:
    """Assign keys by consistent hashing with virtual nodes.

    This is a standard movement-oriented baseline. It should be strong on
    reassignment stability and weak on spatial locality because it ignores the
    coordinates.
    """

    if buckets < 1:
        raise ValueError("buckets must be >= 1")
    if virtual_nodes < 1:
        raise ValueError("virtual_nodes must be >= 1")
    ring: list[tuple[int, int]] = []
    for bucket in range(int(buckets)):
        for vnode in range(int(virtual_nodes)):
            payload = f"{bucket}:{vnode}".encode("ascii")
            digest = hashlib.blake2b(payload, digest_size=8).digest()
            ring.append((int.from_bytes(digest, "little", signed=False), bucket))
    ring.sort(key=lambda item: item[0])
    positions = [item[0] for item in ring]
    labels = []
    for key in keys:
        key_bytes = int(key).to_bytes(8, "little", signed=False)
        digest = hashlib.blake2b(key_bytes, digest_size=8).digest()
        pos = int.from_bytes(digest, "little", signed=False)
        idx = bisect.bisect_left(positions, pos)
        if idx == len(ring):
            idx = 0
        labels.append(ring[idx][1])
    return np.asarray(labels, dtype=np.int64)


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


def _xy_to_hilbert_index(x: int, y: int, bits: int = 16) -> int:
    """Return a 2D Hilbert index for integer coordinates.

    The implementation follows the standard iterative xy-to-d transform for a
    square grid of side ``2**bits``.
    """

    n = 1 << bits
    d = 0
    s = n >> 1
    while s > 0:
        rx = 1 if (x & s) else 0
        ry = 1 if (y & s) else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x = n - 1 - x
                y = n - 1 - y
            x, y = y, x
        s >>= 1
    return int(d)


def hilbert_codes(points: np.ndarray, bits: int = 16) -> np.ndarray:
    """Compute 2D Hilbert order codes for the first two point dimensions."""

    x = np.asarray(points, dtype=float)
    if x.shape[1] < 2:
        x = np.column_stack([x[:, 0], np.zeros(x.shape[0])])
    mins = np.min(x[:, :2], axis=0)
    span = np.maximum(np.ptp(x[:, :2], axis=0), 1e-12)
    norm = np.clip((x[:, :2] - mins) / span, 0, 0.999999)
    max_coord = (1 << bits) - 1
    quant = np.floor(norm * max_coord).astype(np.int64)
    return np.asarray([_xy_to_hilbert_index(int(px), int(py), bits=bits) for px, py in quant], dtype=object)


def hilbert_sort_partition(points: np.ndarray, buckets: int) -> np.ndarray:
    """Locality baseline using contiguous chunks along Hilbert order."""

    return _order_chunk_partition(hilbert_codes(points), buckets)


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


def _order_chunk_partition(codes: np.ndarray, buckets: int) -> np.ndarray:
    order = np.argsort(codes, kind="mergesort")
    ranks = np.empty(len(order), dtype=np.int64)
    ranks[order] = np.arange(len(order))
    labels = np.floor(ranks * buckets / max(1, len(order))).astype(np.int64)
    return np.minimum(labels, buckets - 1)


def _points_to_lat_lon(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map arbitrary 2D points into valid latitude/longitude ranges.

    The geospatial baselines are included as mature hierarchical-cell
    comparisons. Synthetic datasets are normalized into geographic coordinate
    ranges so these baselines can be exercised without requiring real lat/lon
    input.
    """

    x = np.asarray(points, dtype=float)
    if x.shape[1] < 2:
        x = np.column_stack([x[:, 0], np.zeros(x.shape[0])])
    mins = np.min(x[:, :2], axis=0)
    span = np.maximum(np.ptp(x[:, :2], axis=0), 1e-12)
    norm = np.clip((x[:, :2] - mins) / span, 0, 1)
    lat = -85.0 + norm[:, 1] * 170.0
    lon = -180.0 + norm[:, 0] * 360.0
    return lat, lon


def h3_sort_partition(points: np.ndarray, buckets: int, resolution: int = 5) -> np.ndarray:
    """H3 hierarchical-cell ordering baseline.

    Requires the optional ``h3`` package. The partition sorts points by H3 cell
    id and then forms equal-size chunks.
    """

    try:
        import h3  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised when optional dep absent
        raise ImportError("h3_sort_partition requires the optional h3 package") from exc
    lat, lon = _points_to_lat_lon(points)
    codes = np.asarray([h3.latlng_to_cell(float(a), float(o), resolution) for a, o in zip(lat, lon)], dtype=object)
    return _order_chunk_partition(codes, buckets)


def s2_sort_partition(points: np.ndarray, buckets: int, level: int = 10) -> np.ndarray:
    """S2 hierarchical-cell ordering baseline.

    Requires the optional ``s2sphere`` package.
    """

    try:
        from s2sphere import CellId, LatLng  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("s2_sort_partition requires the optional s2sphere package") from exc
    lat, lon = _points_to_lat_lon(points)
    codes = np.asarray([
        int(CellId.from_lat_lng(LatLng.from_degrees(float(a), float(o))).parent(level).id())
        for a, o in zip(lat, lon)
    ], dtype=object)
    return _order_chunk_partition(codes, buckets)


def geohash_sort_partition(points: np.ndarray, buckets: int, precision: int = 5) -> np.ndarray:
    """Geohash ordering baseline.

    Requires the optional ``pygeohash`` package.
    """

    try:
        import pygeohash  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("geohash_sort_partition requires the optional pygeohash package") from exc
    lat, lon = _points_to_lat_lon(points)
    codes = np.asarray([pygeohash.encode(float(a), float(o), precision=precision) for a, o in zip(lat, lon)], dtype=object)
    return _order_chunk_partition(codes, buckets)


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
    labels1 = virtual_node_consistent_hash_labels(keys, k1)
    labels2 = virtual_node_consistent_hash_labels(keys, k2)
    assign = perf_counter() - start
    results["virtual_node_hash"] = PartitionBenchmarkResult(
        "virtual_node_hash", dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
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
        "hilbert_sort": hilbert_sort_partition,
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

    for name, func in {
        "h3_sort": h3_sort_partition,
        "s2_sort": s2_sort_partition,
        "geohash_sort": geohash_sort_partition,
    }.items():
        try:
            start = perf_counter()
            labels1 = func(x, k1)
            labels2 = func(x, k2)
            assign = perf_counter() - start
        except ImportError:
            continue
        results[name] = PartitionBenchmarkResult(
            name, dataset, len(x), k1, k2, movement_fraction(labels1, labels2),
            load_imbalance(labels2), locality_dispersion(x, labels2), 0.0, assign,
        )
    return results
