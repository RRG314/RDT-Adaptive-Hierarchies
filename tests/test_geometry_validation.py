from rdt_adaptive_hierarchy.applications.geometry_validation import run_geometry_validation


def test_recursive_depth_geometry_known_forms_are_bounded():
    rows = run_geometry_validation([1.0])
    rdt = next(row for row in rows if row.method == "rdt_recursive_depth")
    baseline = next(row for row in rows if row.method == "coarse_midpoint_baseline")

    assert rdt.max_relative_error < 0.001
    assert rdt.max_relative_error < baseline.max_relative_error
