import numpy as np

from rdt_adaptive_hierarchy.baselines import (
    geohash_sort_partition,
    grid_partition,
    h3_sort_partition,
    halton_cover,
    hilbert_sort_partition,
    hypothesis_cover,
    jump_consistent_hash,
    morton_sort_partition,
    random_uniform_cover,
    rendezvous_hash,
    s2_sort_partition,
    sobol_cover,
    virtual_node_consistent_hash_labels,
)


def test_hash_baselines_return_valid_bucket_ids():
    for buckets in [1, 4, 17]:
        assert 0 <= jump_consistent_hash(12345, buckets) < buckets
        assert 0 <= rendezvous_hash(12345, buckets) < buckets


def test_spatial_baselines_return_expected_shapes():
    points = np.array([[0.0, 0.0], [0.1, 0.2], [0.9, 0.8], [1.0, 1.0]])
    assert grid_partition(points, 3).shape == (4,)
    assert morton_sort_partition(points, 3).shape == (4,)
    assert hilbert_sort_partition(points, 3).shape == (4,)


def test_optional_geospatial_baselines_return_expected_shapes_when_installed():
    points = np.array([[0.0, 0.0], [0.1, 0.2], [0.9, 0.8], [1.0, 1.0]])
    for func in [h3_sort_partition, s2_sort_partition, geohash_sort_partition]:
        try:
            labels = func(points, 3)
        except ImportError:
            continue
        assert labels.shape == (4,)
        assert labels.min() >= 0
        assert labels.max() < 3


def test_sampling_baselines_return_requested_budget():
    bounds = [(-1.0, 1.0), (-2.0, 2.0)]
    assert random_uniform_cover(bounds, 16, seed=0).shape == (16, 2)
    assert sobol_cover(bounds, 16, seed=0).shape == (16, 2)
    assert halton_cover(bounds, 16, seed=0).shape == (16, 2)


def test_virtual_node_hash_and_hypothesis_cover_run():
    keys = [1, 2, 3, 4]
    labels = virtual_node_consistent_hash_labels(keys, 3, virtual_nodes=8)
    assert labels.shape == (4,)
    assert labels.min() >= 0
    assert labels.max() < 3

    try:
        points = hypothesis_cover([(-1e6, 1e6), (-1e6, 1e6)], 32, seed=0)
    except ImportError:
        return
    assert points.shape == (32, 2)
