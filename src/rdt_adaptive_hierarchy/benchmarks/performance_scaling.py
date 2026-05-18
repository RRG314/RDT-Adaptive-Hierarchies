"""Runtime and memory scaling checks for the public benchmark suites."""

from __future__ import annotations

import argparse
import csv
import json
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from typing import List

from ..applications.cover import benchmark_cover_methods
from ..applications.stable_partition import benchmark_partition_methods
from .memory import process_rss_kib
from .stable_partition_bench import make_spatial_dataset


def run(output_dir: Path, stable_sizes: List[int], cover_budgets: List[int]) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    stable_rows: list[dict] = []
    cover_rows: list[dict] = []

    for n in stable_sizes:
        points = make_spatial_dataset("uniform", n=n, seed=0)
        tracemalloc.start()
        rss_start_kib = process_rss_kib()
        for result in benchmark_partition_methods(points, dataset="uniform", k1=16, k2=20, seed=0).values():
            row = {"suite": "stable_partition_scaling", "n": n, **asdict(result)}
            row["combined_score_lower_is_better"] = (
                row["movement"] + 0.45 * row["locality_k2"] + 0.20 * max(0.0, row["imbalance_k2"] - 1.0)
            )
            row["python_peak_memory_kib"] = float(tracemalloc.get_traced_memory()[1] / 1024.0)
            row["process_rss_kib"] = process_rss_kib()
            row["process_rss_delta_kib"] = max(0.0, row["process_rss_kib"] - rss_start_kib)
            stable_rows.append(row)
        tracemalloc.stop()

    bounds = [(-1e6, 1e6), (-1e6, 1e6)]
    for budget in cover_budgets:
        tracemalloc.start()
        rss_start_kib = process_rss_kib()
        for result in benchmark_cover_methods(bounds, budget=budget, seed=0).values():
            row = {"suite": "cover_scaling", **asdict(result)}
            row["python_peak_memory_kib"] = float(tracemalloc.get_traced_memory()[1] / 1024.0)
            row["process_rss_kib"] = process_rss_kib()
            row["process_rss_delta_kib"] = max(0.0, row["process_rss_kib"] - rss_start_kib)
            cover_rows.append(row)
        tracemalloc.stop()

    result = {
        "benchmark": "performance_scaling",
        "stable_rows": stable_rows,
        "cover_rows": cover_rows,
        "stable_summary": _stable_summary(stable_rows),
        "cover_summary": _cover_summary(cover_rows),
    }
    (output_dir / "performance_scaling_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_csv(output_dir / "stable_partition_scaling.csv", stable_rows)
    _write_csv(output_dir / "cover_scaling.csv", cover_rows)
    (output_dir / "PERFORMANCE_SCALING_RESULT_CARD.md").write_text(_render_markdown(result), encoding="utf-8")
    return result


def _stable_summary(rows: list[dict]) -> list[dict]:
    out = []
    for n in sorted({row["n"] for row in rows}):
        group = [row for row in rows if row["n"] == n]
        fastest = min(group, key=lambda row: row["build_seconds"] + row["assign_seconds"])
        best_score = min(group, key=lambda row: row["combined_score_lower_is_better"])
        rdt = next(row for row in group if row["method"] == "rdt_stable")
        out.append({
            "n": n,
            "best_score_method": best_score["method"],
            "fastest_method": fastest["method"],
            "rdt_seconds": rdt["build_seconds"] + rdt["assign_seconds"],
            "fastest_seconds": fastest["build_seconds"] + fastest["assign_seconds"],
            "rdt_score": rdt["combined_score_lower_is_better"],
            "best_score": best_score["combined_score_lower_is_better"],
            "peak_python_memory_kib": max(row["python_peak_memory_kib"] for row in group),
            "peak_rss_kib": max(row["process_rss_kib"] for row in group),
            "peak_rss_delta_kib": max(row["process_rss_delta_kib"] for row in group),
        })
    return out


def _cover_summary(rows: list[dict]) -> list[dict]:
    out = []
    for budget in sorted({row["budget"] for row in rows}):
        group = [row for row in rows if row["budget"] == budget]
        best_classes = max(group, key=lambda row: (row["discovered_bug_classes"], row["total_hits"]))
        fastest = min(group, key=lambda row: row["runtime_seconds"])
        rdt = next(row for row in group if row["method"] == "rdt_cover")
        out.append({
            "budget": budget,
            "best_discovery_method": best_classes["method"],
            "fastest_method": fastest["method"],
            "rdt_seconds": rdt["runtime_seconds"],
            "fastest_seconds": fastest["runtime_seconds"],
            "rdt_bug_classes": rdt["discovered_bug_classes"],
            "best_bug_classes": best_classes["discovered_bug_classes"],
            "peak_python_memory_kib": max(row["python_peak_memory_kib"] for row in group),
            "peak_rss_kib": max(row["process_rss_kib"] for row in group),
            "peak_rss_delta_kib": max(row["process_rss_delta_kib"] for row in group),
        })
    return out


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _render_markdown(result: dict) -> str:
    lines = [
        "# Performance Scaling Result Card",
        "",
        "These are safe local scaling checks, not production profiling. Memory includes Python `tracemalloc` peak memory and process resident-set-size snapshots.",
        "",
        "## Stable partition",
        "",
        "| N | Best score method | Fastest method | RDT seconds | Fastest seconds | RDT score | Best score | Peak RSS KiB | RSS delta KiB |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["stable_summary"]:
        lines.append(
            f"| {row['n']} | `{row['best_score_method']}` | `{row['fastest_method']}` | {row['rdt_seconds']:.4f} | "
            f"{row['fastest_seconds']:.4f} | {row['rdt_score']:.4f} | {row['best_score']:.4f} | "
            f"{row['peak_rss_kib']:.0f} | {row['peak_rss_delta_kib']:.0f} |"
        )
    lines.extend([
        "",
        "## RDT-cover",
        "",
        "| Budget | Best discovery method | Fastest method | RDT seconds | Fastest seconds | RDT classes | Best classes | Peak RSS KiB | RSS delta KiB |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in result["cover_summary"]:
        lines.append(
            f"| {row['budget']} | `{row['best_discovery_method']}` | `{row['fastest_method']}` | {row['rdt_seconds']:.4f} | "
            f"{row['fastest_seconds']:.4f} | {row['rdt_bug_classes']} | {row['best_bug_classes']} | "
            f"{row['peak_rss_kib']:.0f} | {row['peak_rss_delta_kib']:.0f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run safe performance-scaling checks.")
    parser.add_argument("--output-dir", default="results/tmp/performance_scaling")
    parser.add_argument("--stable-sizes", default="1000,5000,20000")
    parser.add_argument("--cover-budgets", default="128,256,512,1024")
    args = parser.parse_args()
    stable_sizes = [int(part) for part in args.stable_sizes.split(",") if part.strip()]
    cover_budgets = [int(part) for part in args.cover_budgets.split(",") if part.strip()]
    run(Path(args.output_dir), stable_sizes=stable_sizes, cover_budgets=cover_budgets)
    print(f"Wrote performance scaling results to {args.output_dir}")


if __name__ == "__main__":
    main()
