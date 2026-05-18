"""Command-line benchmark for stable partition resize behavior."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..applications.stable_partition import benchmark_partition_methods


def make_spatial_dataset(name: str, n: int = 5_000, seed: int = 0) -> np.ndarray:
    """Create deterministic spatial datasets used by the partition benchmark."""

    rng = np.random.default_rng(seed)
    if name == "uniform":
        return rng.random((n, 2))
    if name == "clustered":
        centers = np.array([[0.2, 0.2], [0.78, 0.3], [0.45, 0.82]])
        labels = rng.integers(0, len(centers), size=n)
        return np.clip(centers[labels] + rng.normal(0, 0.055, size=(n, 2)), 0, 1)
    if name == "diagonal":
        t = rng.random(n)
        return np.clip(np.column_stack([t, t + rng.normal(0, 0.025, size=n)]), 0, 1)
    raise ValueError(f"unknown dataset {name!r}")


def run(output_dir: Path, seeds: int = 3, n: int = 5_000) -> Dict[str, object]:
    """Run stable partition benchmarks and write JSON/CSV/Markdown artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    for seed in range(seeds):
        for dataset in ["uniform", "clustered", "diagonal"]:
            points = make_spatial_dataset(dataset, n=n, seed=seed)
            for result in benchmark_partition_methods(points, dataset=dataset, k1=16, k2=20).values():
                row = {"seed": seed, **asdict(result)}
                row["combined_score_lower_is_better"] = (
                    row["movement"] + 0.45 * row["locality_k2"] + 0.20 * max(0.0, row["imbalance_k2"] - 1.0)
                )
                rows.append(row)
    summary = _summarize(rows)
    result = {"benchmark": "stable_partition", "rows": rows, "summary": summary}
    (output_dir / "stable_partition_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_csv(output_dir / "stable_partition_summary.csv", rows)
    (output_dir / "STABLE_PARTITION_RESULT_CARD.md").write_text(_render_markdown(summary), encoding="utf-8")
    return result


def _summarize(rows: List[dict]) -> List[dict]:
    out: List[dict] = []
    for dataset in sorted({row["dataset"] for row in rows}):
        for method in sorted({row["method"] for row in rows}):
            group = [row for row in rows if row["dataset"] == dataset and row["method"] == method]
            if not group:
                continue
            out.append({
                "dataset": dataset,
                "method": method,
                "runs": len(group),
                "movement_mean": float(np.mean([row["movement"] for row in group])),
                "locality_mean": float(np.mean([row["locality_k2"] for row in group])),
                "imbalance_mean": float(np.mean([row["imbalance_k2"] for row in group])),
                "combined_score_mean": float(np.mean([row["combined_score_lower_is_better"] for row in group])),
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
        "# Stable Partition Result Card",
        "",
        "Lower combined score is better. The score is movement + 0.45 * locality + 0.20 * load penalty.",
        "",
        "| Dataset | Best method | RDT score | Jump score | Morton score |",
        "|---|---|---:|---:|---:|",
    ]
    for dataset in sorted({row["dataset"] for row in summary}):
        group = [row for row in summary if row["dataset"] == dataset]
        best = min(group, key=lambda row: row["combined_score_mean"])
        rdt = next(row for row in group if row["method"] == "rdt_stable")
        jump = next(row for row in group if row["method"] == "jump_hash")
        morton = next(row for row in group if row["method"] == "morton_sort")
        lines.append(
            f"| {dataset} | `{best['method']}` | {rdt['combined_score_mean']:.4f} | "
            f"{jump['combined_score_mean']:.4f} | {morton['combined_score_mean']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the stable partition benchmark.")
    parser.add_argument("--output-dir", default="results/tmp/stable_partition")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--n", type=int, default=5_000)
    args = parser.parse_args()
    run(Path(args.output_dir), seeds=args.seeds, n=args.n)
    print(f"Wrote stable partition benchmark results to {args.output_dir}")


if __name__ == "__main__":
    main()
