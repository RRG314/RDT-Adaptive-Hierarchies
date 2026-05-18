import numpy as np

from rdt_adaptive_hierarchy.applications.stable_partition import RDTStablePartition, jump_consistent_hash, stable_key_from_index
from rdt_adaptive_hierarchy.core.metrics import locality_dispersion, movement_fraction


def test_stable_label_inheritance_has_lower_movement_than_hash_resize_on_uniform_data():
    rng = np.random.default_rng(2)
    x = rng.random((1000, 2))
    rdt = RDTStablePartition(max_buckets=64).fit(x)
    rdt_move = rdt.movement(16, 20)
    keys = [stable_key_from_index(i) for i in range(len(x))]
    h16 = np.array([jump_consistent_hash(k, 16) for k in keys])
    h20 = np.array([jump_consistent_hash(k, 20) for k in keys])
    assert rdt_move < movement_fraction(h16, h20)


def test_stable_labels_are_more_local_than_shuffled_same_counts():
    rng = np.random.default_rng(3)
    x = rng.random((1200, 2))
    rdt = RDTStablePartition(max_buckets=64).fit(x)
    labels = rdt.assign_training(20)
    shuffled = labels.copy()
    rng.shuffle(shuffled)
    assert locality_dispersion(x, labels) < locality_dispersion(x, shuffled)

