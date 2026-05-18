from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

from ..applications.geometry_validation import run_geometry_validation, run_integral_validation


def run_geometry_benchmark(output: Path) -> dict:
    """Run known-form recursive-depth geometry validation."""

    output.mkdir(parents=True, exist_ok=True)
    rows = [row.to_dict() for row in run_geometry_validation()]
    integral_rows = [row.to_dict() for row in run_integral_validation()]
    aggregate = {
        "benchmark": "known_form_geometry_validation",
        "status": "experimental_application_supported_by_known_form_checks",
        "rows": rows,
        "integral_rows": integral_rows,
        "summary": _summary(rows),
        "integral_summary": _integral_summary(integral_rows),
    }
    (output / "geometry_results.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    _write_csv(output / "geometry_summary.csv", rows)
    _write_integral_csv(output / "geometry_integral_summary.csv", integral_rows)
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


def _integral_summary(rows: list[dict]) -> dict:
    out = {}
    for target in sorted({row["target"] for row in rows}):
        group = [row for row in rows if row["target"] == target]
        best = min(group, key=lambda row: row["relative_error"])
        out[target] = {
            "best_method": best["method"],
            "best_relative_error": float(best["relative_error"]),
            "rdt_relative_error": float(next(row["relative_error"] for row in group if row["method"] == "rdt_recursive_depth_grid")),
            "sobol_relative_error": float(next(row["relative_error"] for row in group if row["method"] == "sobol_qmc")),
            "monte_carlo_relative_error": float(next(row["relative_error"] for row in group if row["method"] == "monte_carlo")),
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


def _write_integral_csv(path: Path, rows: list[dict]) -> None:
    fields = ["target", "method", "budget", "estimate", "exact", "absolute_error", "relative_error"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


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
        "## Simple integral checks",
        "",
        "| Target | Best method | RDT relative error | Sobol relative error | Monte Carlo relative error |",
        "|---|---|---:|---:|---:|",
    ])
    for target, row in result["integral_summary"].items():
        lines.append(
            f"| {target} | `{row['best_method']}` | {row['rdt_relative_error']:.6f} | "
            f"{row['sobol_relative_error']:.6f} | {row['monte_carlo_relative_error']:.6f} |"
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
