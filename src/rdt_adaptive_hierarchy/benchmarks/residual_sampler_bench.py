"""Command-line benchmark for the research-only residual sampler."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..applications.residual_sampler import benchmark_residual_samplers, evaluate_selection, RDTResidualSampler, RDTTunedResidualSampler


def make_candidate_grid(n_side: int = 64) -> np.ndarray:
    xs = np.linspace(0, 1, n_side)
    xx, yy = np.meshgrid(xs, xs)
    return np.column_stack([xx.ravel(), yy.ravel()])


def run(output_dir: Path, seeds: int = 3, n_side: int = 64) -> Dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    grid = make_candidate_grid(n_side)
    for seed in range(seeds):
        for field in ["sharp_front", "two_hotspots", "oscillatory", "multi_front"]:
            for result in benchmark_residual_samplers(grid, field=field, seed=seed, n_new=256).values():
                rows.append({"seed": seed, **asdict(result)})
        try:
            points, residuals, gradients = make_california_residual_field(seed=seed)
        except Exception:
            points = residuals = gradients = None
        if points is not None:
            for result in benchmark_residual_samplers_from_values(points, residuals, gradients, field="california_residual", seed=seed, n_new=512).values():
                rows.append({"seed": seed, **asdict(result)})
    summary = _summarize(rows)
    result = {"benchmark": "residual_sampler", "status": "research_only", "rows": rows, "summary": summary}
    (output_dir / "residual_sampler_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_csv(output_dir / "residual_sampler_summary.csv", rows)
    (output_dir / "RESIDUAL_SAMPLER_RESULT_CARD.md").write_text(_render_markdown(summary), encoding="utf-8")
    return result


def _summarize(rows: List[dict]) -> List[dict]:
    out: List[dict] = []
    for field in sorted({row["field"] for row in rows}):
        for method in sorted({row["method"] for row in rows}):
            group = [row for row in rows if row["field"] == field and row["method"] == method]
            if group:
                out.append({
                    "field": field,
                    "method": method,
                    "runs": len(group),
                    "composite_mean": float(np.mean([row["composite_score"] for row in group])),
                    "composite_ci95": _ci95([row["composite_score"] for row in group]),
                    "top_recall_mean": float(np.mean([row["top_recall"] for row in group])),
                    "coverage_entropy_mean": float(np.mean([row["coverage_entropy"] for row in group])),
                })
    return out


def _ci95(values: List[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(1.96 * np.std(values, ddof=1) / np.sqrt(len(values)))


def make_california_residual_field(seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    from sklearn.datasets import fetch_california_housing  # type: ignore
    from sklearn.linear_model import Ridge  # type: ignore
    from sklearn.preprocessing import StandardScaler  # type: ignore

    data = fetch_california_housing()
    x_all = data.data
    y = data.target
    model_x = StandardScaler().fit_transform(x_all)
    model = Ridge(alpha=1.0).fit(model_x, y)
    residuals = np.abs(y - model.predict(model_x))
    residuals = residuals / max(float(np.max(residuals)), 1e-12)
    points = x_all[:, [6, 7]]
    rng = np.random.default_rng(seed)
    if len(points) > 6_000:
        idx = rng.choice(len(points), size=6_000, replace=False)
        points = points[idx]
        residuals = residuals[idx]
    mins = np.min(points, axis=0)
    span = np.maximum(np.ptp(points, axis=0), 1e-12)
    points = (points - mins) / span
    gradients = residuals.copy()
    return points, residuals, gradients


def benchmark_residual_samplers_from_values(
    points: np.ndarray,
    residuals: np.ndarray,
    gradients: np.ndarray,
    field: str,
    seed: int,
    n_new: int,
) -> Dict[str, object]:
    from time import perf_counter

    rng = np.random.default_rng(seed)
    results: Dict[str, object] = {}
    methods = {
        "rdt_residual": lambda: RDTResidualSampler(random_state=seed).select(points, residuals, gradients, n_new=n_new),
        "rdt_no_coverage": lambda: RDTResidualSampler(exploration_fraction=0.0, random_state=seed).select(points, residuals, gradients, n_new=n_new),
        "rdt_no_gradient": lambda: RDTResidualSampler(gradient_weight=0.0, random_state=seed).select(points, residuals, None, n_new=n_new),
        "rdt_residual_tuned": lambda: RDTTunedResidualSampler(random_state=seed).select(points, residuals, gradients, n_new=n_new),
        "uniform": lambda: rng.choice(len(points), size=n_new, replace=False),
        "top_residual": lambda: np.argsort(residuals)[-n_new:],
        "top_residual_gradient": lambda: np.argsort(residuals + 0.35 * gradients)[-n_new:],
        "residual_proportional": lambda: rng.choice(len(points), size=n_new, replace=False, p=(residuals + 1e-9) / np.sum(residuals + 1e-9)),
    }
    for name, func in methods.items():
        start = perf_counter()
        selected = func()
        results[name] = evaluate_selection(points, residuals, selected, name, field, perf_counter() - start)
    return results


def _write_csv(path: Path, rows: List[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _render_markdown(summary: List[dict]) -> str:
    lines = [
        "# Residual Sampler Result Card",
        "",
        "This benchmark is research-only. It tests point selection metrics, not full PDE or PINN training.",
        "",
        "| Field | Best method | RDT tuned | Top residual | Uniform |",
        "|---|---|---:|---:|---:|",
    ]
    for field in sorted({row["field"] for row in summary}):
        group = [row for row in summary if row["field"] == field]
        best = max(group, key=lambda row: row["composite_mean"])
        tuned = next(row for row in group if row["method"] == "rdt_residual_tuned")
        top = next(row for row in group if row["method"] == "top_residual")
        uniform = next(row for row in group if row["method"] == "uniform")
        lines.append(
            f"| {field} | `{best['method']}` | {tuned['composite_mean']:.4f} | "
            f"{top['composite_mean']:.4f} | {uniform['composite_mean']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the residual sampler benchmark.")
    parser.add_argument("--output-dir", default="results/tmp/residual_sampler")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--n-side", type=int, default=64)
    args = parser.parse_args()
    run(Path(args.output_dir), seeds=args.seeds, n_side=args.n_side)
    print(f"Wrote residual sampler benchmark results to {args.output_dir}")


if __name__ == "__main__":
    main()
