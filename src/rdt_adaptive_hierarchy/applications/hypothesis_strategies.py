from __future__ import annotations

from typing import List, Tuple


def numeric_point_strategy(bounds: List[Tuple[float, float]]):
    """Return a Hypothesis strategy for bounded numeric points.

    This is a public integration helper for users who want to compare
    RDT-cover with property-based testing. It deliberately does not know the
    benchmark predicates; predicate-aware searches belong in tests or benchmark
    code where the property is explicit.
    """

    try:
        from hypothesis import strategies as st  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("numeric_point_strategy requires the optional hypothesis package") from exc

    finite_bounds = [(float(low), float(high)) for low, high in bounds]
    return st.tuples(*[
        st.floats(min_value=low, max_value=high, allow_nan=False, allow_infinity=False, width=64)
        for low, high in finite_bounds
    ])


def edge_aware_numeric_point_strategy(bounds: List[Tuple[float, float]]):
    """Return a Hypothesis strategy with common numerical edge anchors.

    This strategy includes regular bounded floats and sampled anchors such as
    zero, boundaries, powers of two, and powers of ten. It is useful as a
    property-based baseline for RDT-cover, but it still requires the caller to
    provide the property being tested.
    """

    try:
        from hypothesis import strategies as st  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("edge_aware_numeric_point_strategy requires the optional hypothesis package") from exc

    finite_bounds = [(float(low), float(high)) for low, high in bounds]

    per_dim = []
    for low, high in finite_bounds:
        anchors = [low, high, (low + high) / 2.0]
        if low <= 0 <= high:
            anchors.append(0.0)
        for exponent in range(-12, 13):
            anchors.extend([10.0**exponent, -(10.0**exponent), 2.0**exponent, -(2.0**exponent)])
        anchors = sorted({float(value) for value in anchors if low <= value <= high})
        per_dim.append(st.one_of(
            st.floats(min_value=low, max_value=high, allow_nan=False, allow_infinity=False, width=64),
            st.sampled_from(anchors),
        ))
    base = st.tuples(*per_dim)
    if len(finite_bounds) < 2:
        return base

    @st.composite
    def cancellation_pair(draw):
        values = list(draw(base))
        magnitude = draw(st.sampled_from([1e3, 1e4, 1e5, 1e6]))
        sign = draw(st.sampled_from([-1.0, 1.0]))
        x = sign * magnitude
        low0, high0 = finite_bounds[0]
        low1, high1 = finite_bounds[1]
        values[0] = min(max(x, low0), high0)
        values[1] = min(max(-values[0], low1), high1)
        return tuple(float(value) for value in values)

    return st.one_of(base, cancellation_pair())
