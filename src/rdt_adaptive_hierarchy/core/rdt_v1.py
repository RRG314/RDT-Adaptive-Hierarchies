from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import floor, log
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


def rdt_depth_int(n: int) -> int:
    """Integer floor-log recursive depth.

    This is the discrete depth observable used by several RDT notebooks. It is
    intentionally modest: a stopping-time statistic, not a theory by itself.
    """

    n = int(abs(n))
    if n <= 1:
        return 0
    depth = 0
    while n > 1:
        divisor = max(2, floor(log(n + 1)))
        n = n // divisor
        depth += 1
        if depth > 10_000:
            raise RuntimeError("rdt_depth_int did not converge")
    return depth


@dataclass(frozen=True)
class RDTNode:
    node_id: int
    parent_id: Optional[int]
    depth: int
    indices: np.ndarray
    split_dim: Optional[int] = None
    threshold: Optional[float] = None
    left_id: Optional[int] = None
    right_id: Optional[int] = None
    bucket_label: Optional[int] = None
    split_order: Optional[int] = None

    @property
    def size(self) -> int:
        return int(self.indices.size)


class RDTHierarchy:
    """Deterministic adaptive binary hierarchy over points.

    The splitter chooses the highest-spread dimension and splits at the median.
    It is intentionally simple so that benchmark results can be attributed to
    the hierarchy/ancestor mechanism rather than to a hidden learned model.
    """

    def __init__(self, max_leaves: int = 64, min_leaf_size: int = 8, max_depth: int = 32):
        if max_leaves < 1:
            raise ValueError("max_leaves must be >= 1")
        self.max_leaves = int(max_leaves)
        self.min_leaf_size = int(min_leaf_size)
        self.max_depth = int(max_depth)
        self.points: Optional[np.ndarray] = None
        self.nodes: Dict[int, RDTNode] = {}
        self.split_sequence: List[int] = []
        self._next_node_id = 1
        self._active_cache: Dict[int, Dict[int, int]] = {}
        self._label_cache: Dict[int, np.ndarray] = {}

    def fit(self, points: np.ndarray) -> "RDTHierarchy":
        x = np.asarray(points, dtype=float)
        if x.ndim != 2:
            raise ValueError("points must be a 2D array")
        if x.shape[0] == 0:
            raise ValueError("points must not be empty")
        self.points = x
        self.nodes = {0: RDTNode(node_id=0, parent_id=None, depth=0, indices=np.arange(x.shape[0]))}
        self.split_sequence = []
        self._next_node_id = 1
        self._active_cache = {}
        self._label_cache = {}

        active = {0}
        heap: List[Tuple[float, int]] = []
        heappush(heap, (-self._priority(0), 0))
        bucket_count = 1

        while bucket_count < self.max_leaves and heap:
            _, node_id = heappop(heap)
            if node_id not in active:
                continue
            if not self._can_split(node_id):
                continue
            left, right = self._split_node(node_id, split_order=len(self.split_sequence))
            active.remove(node_id)
            active.add(left)
            active.add(right)
            self.split_sequence.append(node_id)
            bucket_count += 1
            heappush(heap, (-self._priority(left), left))
            heappush(heap, (-self._priority(right), right))
        return self

    def _priority(self, node_id: int) -> float:
        assert self.points is not None
        node = self.nodes[node_id]
        pts = self.points[node.indices]
        if pts.shape[0] <= 1:
            return 0.0
        spread = float(np.max(np.ptp(pts, axis=0)))
        return node.size * max(spread, 1e-12)

    def _can_split(self, node_id: int) -> bool:
        node = self.nodes[node_id]
        if node.size < max(2, self.min_leaf_size):
            return False
        if node.depth >= self.max_depth:
            return False
        assert self.points is not None
        pts = self.points[node.indices]
        return bool(np.any(np.ptp(pts, axis=0) > 0))

    def _split_node(self, node_id: int, split_order: int) -> Tuple[int, int]:
        assert self.points is not None
        node = self.nodes[node_id]
        pts = self.points[node.indices]
        spreads = np.ptp(pts, axis=0)
        dim = int(np.argmax(spreads))
        values = pts[:, dim]
        # Partition-based median is enough for the hierarchy and avoids full
        # sorting every node during construction.
        half = max(1, min(len(values) - 1, len(values) // 2))
        order = np.argpartition(values, half)
        left_local = order[:half]
        right_local = order[half:]
        left_indices = node.indices[left_local]
        right_indices = node.indices[right_local]
        threshold = float((np.max(values[left_local]) + np.min(values[right_local])) / 2.0)

        left_id = self._next_node_id
        right_id = self._next_node_id + 1
        self._next_node_id += 2

        left = RDTNode(left_id, node_id, node.depth + 1, left_indices)
        right = RDTNode(right_id, node_id, node.depth + 1, right_indices)
        updated = RDTNode(
            node_id=node.node_id,
            parent_id=node.parent_id,
            depth=node.depth,
            indices=node.indices,
            split_dim=dim,
            threshold=threshold,
            left_id=left_id,
            right_id=right_id,
            bucket_label=node.bucket_label,
            split_order=split_order,
        )
        self.nodes[node_id] = updated
        self.nodes[left_id] = left
        self.nodes[right_id] = right
        return left_id, right_id

    def active_nodes(self, bucket_count: int) -> Dict[int, int]:
        """Return active node_id -> stable bucket label for a bucket count."""

        if bucket_count < 1:
            raise ValueError("bucket_count must be >= 1")
        if bucket_count in self._active_cache:
            return dict(self._active_cache[bucket_count])
        split_limit = min(bucket_count - 1, len(self.split_sequence))
        active: Dict[int, int] = {0: 0}
        next_label = 1
        for node_id in self.split_sequence[:split_limit]:
            label = active.pop(node_id)
            node = self.nodes[node_id]
            assert node.left_id is not None and node.right_id is not None
            active[node.left_id] = label
            active[node.right_id] = next_label
            next_label += 1
        self._active_cache[bucket_count] = dict(active)
        return active

    def labels_for_training_points(self, bucket_count: int) -> np.ndarray:
        if self.points is None:
            raise RuntimeError("fit must be called first")
        if bucket_count in self._label_cache:
            return self._label_cache[bucket_count].copy()
        labels = np.empty(self.points.shape[0], dtype=np.int64)
        for node_id, label in self.active_nodes(bucket_count).items():
            labels[self.nodes[node_id].indices] = label
        self._label_cache[bucket_count] = labels.copy()
        return labels

    def assign(self, points: np.ndarray, bucket_count: int) -> np.ndarray:
        x = np.asarray(points, dtype=float)
        active = self.active_nodes(bucket_count)
        labels = np.empty(x.shape[0], dtype=np.int64)
        split_limit = min(bucket_count - 1, len(self.split_sequence))
        split_nodes = set(self.split_sequence[:split_limit])
        for i, row in enumerate(x):
            node_id = 0
            while node_id in split_nodes:
                node = self.nodes[node_id]
                assert node.split_dim is not None and node.threshold is not None
                assert node.left_id is not None and node.right_id is not None
                node_id = node.left_id if row[node.split_dim] <= node.threshold else node.right_id
            labels[i] = active[node_id]
        return labels

    def depth_for_training_points(self, bucket_count: int) -> np.ndarray:
        depths = np.empty(self.points.shape[0], dtype=np.int64) if self.points is not None else None
        if depths is None:
            raise RuntimeError("fit must be called first")
        for node_id in self.active_nodes(bucket_count):
            node = self.nodes[node_id]
            depths[node.indices] = node.depth
        return depths

    def ancestors(self, node_id: int) -> List[int]:
        out = []
        current: Optional[int] = node_id
        while current is not None:
            out.append(current)
            current = self.nodes[current].parent_id
        return list(reversed(out))


def movement_fraction(a: Iterable[int], b: Iterable[int]) -> float:
    aa = np.asarray(a if isinstance(a, np.ndarray) else list(a))
    bb = np.asarray(b if isinstance(b, np.ndarray) else list(b))
    if aa.shape != bb.shape:
        raise ValueError("label arrays must have the same shape")
    return float(np.mean(aa != bb))


def load_imbalance(labels: Iterable[int]) -> float:
    labels = np.asarray(labels if isinstance(labels, np.ndarray) else list(labels), dtype=np.int64)
    counts = np.bincount(labels)
    counts = counts[counts > 0]
    if counts.size == 0:
        return 0.0
    return float(np.max(counts) / np.mean(counts))


def locality_dispersion(points: np.ndarray, labels: Iterable[int]) -> float:
    x = np.asarray(points, dtype=float)
    labels = np.asarray(labels if isinstance(labels, np.ndarray) else list(labels), dtype=np.int64)
    global_var = float(np.mean(np.sum((x - np.mean(x, axis=0)) ** 2, axis=1)))
    if global_var <= 1e-15:
        return 0.0
    if labels.size == 0:
        return 0.0
    max_label = int(np.max(labels))
    counts = np.bincount(labels, minlength=max_label + 1).astype(float)
    sums = np.zeros((max_label + 1, x.shape[1]), dtype=float)
    np.add.at(sums, labels, x)
    sum_sq = np.bincount(labels, weights=np.sum(x * x, axis=1), minlength=max_label + 1)
    nonzero = counts > 0
    within_by_label = sum_sq[nonzero] - np.sum(sums[nonzero] * sums[nonzero], axis=1) / counts[nonzero]
    total_within = float(np.sum(np.maximum(within_by_label, 0.0)))
    return float((total_within / max(1, x.shape[0])) / global_var)


RDTHierarchyV1 = RDTHierarchy

__all__ = [
    "RDTHierarchy",
    "RDTHierarchyV1",
    "RDTNode",
    "load_imbalance",
    "locality_dispersion",
    "movement_fraction",
    "rdt_depth_int",
]
