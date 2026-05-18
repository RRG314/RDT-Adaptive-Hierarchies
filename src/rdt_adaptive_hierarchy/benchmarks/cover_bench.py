"""Command-line benchmark for RDT-cover edge-case generation."""

from __future__ import annotations

import argparse
import csv
import json
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..applications.cover import benchmark_cover_methods, seeded_numeric_bug_predicates


def run(output_dir: Path, seeds: int = 3, budget: int = 512, budgets: List[int] | None = None) -> Dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    bounds = [(-1e6, 1e6), (-1e6, 1e6)]
    if budgets is None:
        budgets = [budget]
    tracemalloc.start()
    for budget_value in budgets:
        for seed in range(seeds):
            for result in benchmark_cover_methods(bounds, budget=budget_value, seed=seed).values():
                rows.append({"seed": seed, **asdict(result), "python_peak_memory_kib": float(tracemalloc.get_traced_memory()[1] / 1024.0)})
    peak_kib = float(tracemalloc.get_traced_memory()[1] / 1024.0)
    tracemalloc.stop()
    summary = _summarize(rows)
    result = {
        "benchmark": "cover",
        "bug_class_count": len(seeded_numeric_bug_predicates(np.zeros((1, 2)))),
        "rows": rows,
        "summary": summary,
        "peak_memory_kib": peak_kib,
    }
    (output_dir / "cover_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_csv(output_dir / "cover_summary.csv", rows)
    (output_dir / "COVER_RESULT_CARD.md").write_text(_render_markdown(summary), encoding="utf-8")
    return result


def _summarize(rows: List[dict]) -> List[dict]:
    out: List[dict] = []
    for budget in sorted({row["budget"] for row in rows}):
        for method in sorted({row["method"] for row in rows}):
            group = [row for row in rows if row["budget"] == budget and row["method"] == method]
            if not group:
                continue
            bug_classes = [row["discovered_bug_classes"] for row in group]
            total_hits = [row["total_hits"] for row in group]
            hit_rates = [row["hit_rate"] for row in group]
            first_hits = [row["first_hit_index"] for row in group if row["first_hit_index"] > 0]
            discrepancies = [row["centered_discrepancy"] for row in group]
            out.append({
                "budget": budget,
                "method": method,
                "runs": len(group),
                "bug_classes_mean": float(np.mean(bug_classes)),
                "bug_classes_ci95": _ci95(bug_classes),
                "total_hits_mean": float(np.mean(total_hits)),
                "total_hits_ci95": _ci95(total_hits),
                "hit_rate_mean": float(np.mean(hit_rates)),
                "first_hit_index_mean": float(np.mean(first_hits)) if first_hits else -1.0,
                "discrepancy_mean": float(np.mean(discrepancies)),
                "discrepancy_ci95": _ci95(discrepancies),
                "python_peak_memory_kib_max": float(max(row.get("python_peak_memory_kib", 0.0) for row in group)),
            })
    return out


def _ci95(values: List[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(1.96 * np.std(values, ddof=1) / np.sqrt(len(values)))


def _write_csv(path: Path, rows: List[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _render_markdown(summary: List[dict]) -> str:
    lines = [
        "# RDT-Cover Result Card",
        "",
        "Higher bug-class discovery is better. Centered discrepancy is reported as a space-filling diagnostic, not the primary RDT-cover objective.",
        "",
        "| Method | Mean bug classes ±95% CI | Mean total hits ±95% CI | Mean discrepancy ±95% CI | Peak Python memory KiB |",
        "|---|---:|---:|---:|---:|",
    ]
    max_budget = max(row["budget"] for row in summary) if summary else 0
    for row in sorted([item for item in summary if item["budget"] == max_budget], key=lambda item: (-item["bug_classes_mean"], -item["total_hits_mean"])):
        lines.append(
            f"| `{row['method']}` | {row['bug_classes_mean']:.2f} ± {row['bug_classes_ci95']:.2f} | "
            f"{row['total_hits_mean']:.2f} ± {row['total_hits_ci95']:.2f} | "
            f"{row['discrepancy_mean']:.5f} ± {row['discrepancy_ci95']:.5f} | "
            f"{row['python_peak_memory_kib_max']:.0f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RDT-cover benchmark.")
    parser.add_argument("--output-dir", default="results/tmp/cover")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--budget", type=int, default=512)
    parser.add_argument("--budgets", type=str, default="", help="Comma-separated budget list; overrides --budget when set.")
    args = parser.parse_args()
    budgets = [int(part) for part in args.budgets.split(",") if part.strip()] if args.budgets else None
    run(Path(args.output_dir), seeds=args.seeds, budget=args.budget, budgets=budgets)
    print(f"Wrote cover benchmark results to {args.output_dir}")


if __name__ == "__main__":
    main()
