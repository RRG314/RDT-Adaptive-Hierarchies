import numpy as np

from rdt_adaptive_hierarchy.baselines import (
    grid_partition,
    jump_consistent_hash,
    morton_sort_partition,
    random_uniform_cover,
    rendezvous_hash,
    sobol_cover,
)


def test_hash_baselines_return_valid_bucket_ids():
    for buckets in [1, 4, 17]:
        assert 0 <= jump_consistent_hash(12345, buckets) < buckets
        assert 0 <= rendezvous_hash(12345, buckets) < buckets


def test_spatial_baselines_return_expected_shapes():
    points = np.array([[0.0, 0.0], [0.1, 0.2], [0.9, 0.8], [1.0, 1.0]])
    assert grid_partition(points, 3).shape == (4,)
    assert morton_sort_partition(points, 3).shape == (4,)


def test_sampling_baselines_return_requested_budget():
    bounds = [(-1.0, 1.0), (-2.0, 2.0)]
    assert random_uniform_cover(bounds, 16, seed=0).shape == (16, 2)
    assert sobol_cover(bounds, 16, seed=0).shape == (16, 2)
