"""Command-line benchmark for RDT-cover edge-case generation."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..applications.cover import benchmark_cover_methods


def run(output_dir: Path, seeds: int = 3, budget: int = 512) -> Dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    bounds = [(-1e6, 1e6), (-1e6, 1e6)]
    for seed in range(seeds):
        for result in benchmark_cover_methods(bounds, budget=budget, seed=seed).values():
            rows.append({"seed": seed, **asdict(result)})
    summary = _summarize(rows)
    result = {"benchmark": "cover", "rows": rows, "summary": summary}
    (output_dir / "cover_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_csv(output_dir / "cover_summary.csv", rows)
    (output_dir / "COVER_RESULT_CARD.md").write_text(_render_markdown(summary), encoding="utf-8")
    return result


def _summarize(rows: List[dict]) -> List[dict]:
    out: List[dict] = []
    for method in sorted({row["method"] for row in rows}):
        group = [row for row in rows if row["method"] == method]
        out.append({
            "method": method,
            "runs": len(group),
            "bug_classes_mean": float(np.mean([row["discovered_bug_classes"] for row in group])),
            "total_hits_mean": float(np.mean([row["total_hits"] for row in group])),
            "discrepancy_mean": float(np.mean([row["centered_discrepancy"] for row in group])),
        })
    return out


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
        "| Method | Mean bug classes | Mean total hits | Mean discrepancy |",
        "|---|---:|---:|---:|",
    ]
    for row in sorted(summary, key=lambda item: (-item["bug_classes_mean"], -item["total_hits_mean"])):
        lines.append(
            f"| `{row['method']}` | {row['bug_classes_mean']:.2f} | "
            f"{row['total_hits_mean']:.2f} | {row['discrepancy_mean']:.5f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RDT-cover benchmark.")
    parser.add_argument("--output-dir", default="results/tmp/cover")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--budget", type=int, default=512)
    args = parser.parse_args()
    run(Path(args.output_dir), seeds=args.seeds, budget=args.budget)
    print(f"Wrote cover benchmark results to {args.output_dir}")


if __name__ == "__main__":
    main()
