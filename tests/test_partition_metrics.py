import numpy as np

from rdt_adaptive_hierarchy.core.metrics import load_imbalance, locality_dispersion, movement_fraction


def test_metric_definitions_on_simple_partition():
    x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    a = np.array([0, 0, 1, 1])
    b = np.array([0, 1, 1, 1])
    assert movement_fraction(a, b) == 0.25
    assert load_imbalance(a) == 1.0
    assert 0.0 <= locality_dispersion(x, a) <= 1.0

