from hypothesis import find, settings

from rdt_adaptive_hierarchy.applications.hypothesis_strategies import edge_aware_numeric_point_strategy


def main() -> None:
    strategy = edge_aware_numeric_point_strategy([(-1e6, 1e6), (-1e6, 1e6)])
    point = find(
        strategy,
        lambda p: abs(p[0] + p[1]) < 1e-6 and max(abs(p[0]), abs(p[1])) > 1e3,
        settings=settings(database=None, deadline=None, max_examples=512),
    )
    print({"status": "found", "large_cancellation_example": tuple(round(v, 6) for v in point)})


if __name__ == "__main__":
    main()
