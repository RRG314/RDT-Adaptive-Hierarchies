from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

from ..applications.geometry_validation import run_geometry_validation


def run_geometry_benchmark(output: Path) -> dict:
    """Run known-form recursive-depth geometry validation."""

    output.mkdir(parents=True, exist_ok=True)
    rows = [row.to_dict() for row in run_geometry_validation()]
    aggregate = {
        "benchmark": "known_form_geometry_validation",
        "status": "experimental_application_supported_by_known_form_checks",
        "rows": rows,
        "summary": _summary(rows),
    }
    (output / "geometry_results.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    _write_csv(output / "geometry_summary.csv", rows)
    (output / "GEOMETRY_RESULT_CARD.md").write_text(_render_markdown(aggregate), encoding="utf-8")
    return aggregate


def _summary(rows: list[dict]) -> dict:
    out = {}
    for method in sorted({row["method"] for row in rows}):
        group = [row for row in rows if row["method"] == method]
        out[method] = {
            "runs": len(group),
            "max_relative_error_mean": mean(float(row["max_relative_error"]) for row in group),
            "mean_relative_error_mean": mean(float(row["mean_relative_error"]) for row in group),
        }
    return out


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = ["radius", "method", "max_relative_error", "mean_relative_error", "relative_errors"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            copied = dict(row)
            copied["relative_errors"] = json.dumps(copied["relative_errors"], sort_keys=True)
            writer.writerow(copied)


def _render_markdown(result: dict) -> str:
    lines = [
        "# Geometry Validation Result Card",
        "",
        "This application checks whether the recursive-depth refinement schedule reproduces known closed forms. It does not establish a new geometry theory.",
        "",
        "| Method | Runs | Mean max relative error | Mean relative error |",
        "|---|---:|---:|---:|",
    ]
    for method, row in result["summary"].items():
        lines.append(
            f"| `{method}` | {row['runs']} | {row['max_relative_error_mean']:.8f} | {row['mean_relative_error_mean']:.8f} |"
        )
    lines.extend([
        "",
        "Status: `experimental_application_supported_by_known_form_checks`.",
        "",
        "Failure condition: recursive-depth refinement fails if it does not converge on the known disk/sphere/cone/cube/cylinder formulas or loses to equal-budget standard quadrature under a predeclared budget.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/geometry")
    args = parser.parse_args()
    output = Path(args.output_dir)
    run_geometry_benchmark(output)
    print(f"Wrote geometry validation results to {output}")


if __name__ == "__main__":
    main()
