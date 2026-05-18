from rdt_adaptive_hierarchy.applications.cover import benchmark_cover_methods, rdt_cover, seeded_numeric_bug_predicates


def test_rdt_cover_finds_seeded_edge_classes():
    bounds = [(-1e6, 1e6), (-1e6, 1e6)]
    points = rdt_cover(bounds, budget=256, seed=0)
    bugs = seeded_numeric_bug_predicates(points)
    assert sum(bool(mask.any()) for mask in bugs.values()) >= 4


def test_hybrid_cover_is_available_and_runs():
    results = benchmark_cover_methods([(-1e6, 1e6), (-1e6, 1e6)], budget=128, seed=0)
    assert "rdt_hybrid_cover" in results
    assert results["rdt_hybrid_cover"].discovered_bug_classes >= 4

