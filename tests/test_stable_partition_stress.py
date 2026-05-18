import numpy as np

from rdt_adaptive_hierarchy.applications.stable_partition import RDTStablePartition
from rdt_adaptive_hierarchy.core.metrics import load_imbalance, locality_dispersion, movement_fraction


def _assert_valid_labels(labels: np.ndarray, n: int, buckets: int) -> None:
    assert labels.shape == (n,)
    assert np.issubdtype(labels.dtype, np.integer)
    assert labels.min() >= 0
    assert labels.max() < buckets


def test_duplicate_points_do_not_break_resize_metrics():
    rng = np.random.default_rng(10)
    unique = rng.random((64, 2))
    repeated = np.repeat(unique, repeats=6, axis=0)
    x = np.vstack([repeated, rng.random((128, 2))])

    partitioner = RDTStablePartition(max_buckets=80, min_leaf_size=4).fit(x)
    labels_16 = partitioner.assign_training(16)
    labels_20 = partitioner.assign_training(20)

    _assert_valid_labels(labels_16, len(x), 16)
    _assert_valid_labels(labels_20, len(x), 20)
    assert 0.0 <= movement_fraction(labels_16, labels_20) <= 1.0
    assert np.isfinite(load_imbalance(labels_20))
    assert np.isfinite(locality_dispersion(x, labels_20))


def test_all_points_same_degeneracy_collapses_without_crashing():
    x = np.ones((256, 2)) * 0.5
    partitioner = RDTStablePartition(max_buckets=32).fit(x)
    labels_8 = partitioner.assign_training(8)
    labels_10 = partitioner.assign_training(10)

    _assert_valid_labels(labels_8, len(x), 8)
    _assert_valid_labels(labels_10, len(x), 10)
    assert np.unique(labels_8).tolist() == [0]
    assert np.unique(labels_10).tolist() == [0]
    assert movement_fraction(labels_8, labels_10) == 0.0
    assert locality_dispersion(x, labels_10) == 0.0


def test_high_dimensional_points_assign_and_score_cleanly():
    rng = np.random.default_rng(11)
    x = rng.normal(size=(900, 32))
    x[:, :4] += rng.integers(0, 4, size=(900, 1))

    partitioner = RDTStablePartition(max_buckets=64).fit(x)
    labels = partitioner.assign_training(40)
    new_labels = partitioner.assign(x[:25] + 1e-6, buckets=40)

    _assert_valid_labels(labels, len(x), 40)
    _assert_valid_labels(new_labels, 25, 40)
    assert np.isfinite(load_imbalance(labels))
    assert np.isfinite(locality_dispersion(x, labels))


def test_adversarial_input_order_changes_little_on_smooth_uniform_data():
    rng = np.random.default_rng(12)
    x = rng.random((1200, 2))
    perm = np.argsort(x[:, 0] + 0.37 * x[:, 1])
    adversarial = x[perm]

    base = RDTStablePartition(max_buckets=64).fit(x)
    ordered = RDTStablePartition(max_buckets=64).fit(adversarial)
    base_score = base.movement(16, 20) + 0.45 * base.locality_score(x, 20)
    ordered_score = ordered.movement(16, 20) + 0.45 * ordered.locality_score(adversarial, 20)

    assert np.isfinite(base_score)
    assert np.isfinite(ordered_score)
    assert abs(base_score - ordered_score) < 0.10
