from rdt_adaptive_hierarchy.applications.hypothesis_strategies import (
    edge_aware_numeric_point_strategy,
    numeric_point_strategy,
)


def test_numeric_point_strategy_can_find_zero_boundary():
    try:
        from hypothesis import find, settings
    except ImportError:
        return

    strategy = edge_aware_numeric_point_strategy([(-1.0, 1.0), (-1.0, 1.0)])
    point = find(strategy, lambda p: abs(p[0]) < 1e-12, settings=settings(database=None, deadline=None))
    assert abs(point[0]) < 1e-12


def test_basic_numeric_strategy_stays_inside_bounds():
    try:
        from hypothesis import find, settings
    except ImportError:
        return

    strategy = numeric_point_strategy([(-2.0, 3.0), (10.0, 11.0)])
    point = find(strategy, lambda p: True, settings=settings(database=None, deadline=None))
    assert -2.0 <= point[0] <= 3.0
    assert 10.0 <= point[1] <= 11.0
