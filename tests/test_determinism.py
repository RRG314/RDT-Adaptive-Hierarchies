import numpy as np

from rdt_adaptive_hierarchy import RDTHierarchy


def test_hierarchy_deterministic_for_fixed_input_order():
    rng = np.random.default_rng(0)
    x = rng.random((300, 2))
    a = RDTHierarchy(max_leaves=32).fit(x)
    b = RDTHierarchy(max_leaves=32).fit(x)
    np.testing.assert_array_equal(a.labels_for_training_points(20), b.labels_for_training_points(20))
    assert a.path(x[10], bucket_count=20) == b.path(x[10], bucket_count=20)


def test_export_import_roundtrip_preserves_assignments():
    rng = np.random.default_rng(1)
    x = rng.random((128, 2))
    h = RDTHierarchy(max_leaves=16).fit(x)
    restored = RDTHierarchy.import_state(h.export_state())
    np.testing.assert_array_equal(h.labels_for_training_points(12), restored.labels_for_training_points(12))

