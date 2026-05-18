import numpy as np

from rdt_adaptive_hierarchy.applications.cover import benchmark_cover_methods
from rdt_adaptive_hierarchy.applications.stable_partition import (
    RDTStablePartition,
    morton_codes,
)
from rdt_adaptive_hierarchy.core.metrics import locality_dispersion, movement_fraction


def test_stable_label_inheritance_beats_remapped_labels_on_simple_resize():
    rng = np.random.default_rng(0)
    points = rng.random((2_000, 2))
    rdt = RDTStablePartition(max_buckets=32).fit(points)
    stable_16 = rdt.assign_training(16)
    stable_20 = rdt.assign_training(20)

    hierarchy = rdt.hierarchy
    active_16 = hierarchy.active_nodes(16)
    active_20 = hierarchy.active_nodes(20)
    remap_16 = _remapped_by_centroid(points, hierarchy, active_16)
    remap_20 = _remapped_by_centroid(points, hierarchy, active_20)

    stable_score = movement_fraction(stable_16, stable_20) + 0.45 * locality_dispersion(points, stable_20)
    remap_score = movement_fraction(remap_16, remap_20) + 0.45 * locality_dispersion(points, remap_20)
    assert stable_score < remap_score


def test_coverage_benchmark_keeps_rdt_edge_advantage():
    results = benchmark_cover_methods([(-1e6, 1e6), (-1e6, 1e6)], budget=256, seed=0)
    assert results["rdt_cover"].discovered_bug_classes > results["sobol"].discovered_bug_classes


def _remapped_by_centroid(points, hierarchy, active):
    centroids = []
    node_ids = list(active.keys())
    for node_id in node_ids:
        centroids.append(np.mean(points[hierarchy.nodes[node_id].indices], axis=0))
    order = np.argsort(morton_codes(np.vstack(centroids)), kind="mergesort")
    labels = np.empty(points.shape[0], dtype=np.int64)
    for new_label, order_idx in enumerate(order):
        node_id = node_ids[int(order_idx)]
        labels[hierarchy.nodes[node_id].indices] = new_label
    return labels
