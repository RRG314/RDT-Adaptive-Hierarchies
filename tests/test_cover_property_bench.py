from rdt_adaptive_hierarchy.benchmarks.cover_property_bench import numeric_properties, run


def test_cover_property_benchmark_writes_summary(tmp_path):
    payload = run(tmp_path, budget=64, seeds=1)

    assert payload["benchmark"] == "cover_property"
    assert (tmp_path / "cover_property_results.json").exists()
    assert (tmp_path / "cover_property_summary.csv").exists()
    assert (tmp_path / "COVER_PROPERTY_RESULT_CARD.md").exists()

    properties = {row["property_name"] for row in payload["rows"]}
    methods = {row["method"] for row in payload["rows"]}
    assert properties == {prop.name for prop in numeric_properties()}
    assert "rdt_cover" in methods
    assert "hypothesis_find" in methods
