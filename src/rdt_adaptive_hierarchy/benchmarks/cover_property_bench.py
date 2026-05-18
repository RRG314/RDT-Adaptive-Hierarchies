"""Numerical property benchmark for RDT-cover.

This benchmark is separate from the seeded edge-class corpus. It checks whether
coverage methods expose failures in ordinary floating-point identities and
roundtrips, then compares them with a targeted Hypothesis search.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

import numpy as np

from ..applications.cover import (
    boundary_only_cover,
    halton_cover,
    latin_hypercube_cover,
    powers_only_cover,
    random_uniform_cover,
    rdt_cover,
    rdt_hybrid_cover,
    sobol_cover,
)
from ..applications.hypothesis_strategies import edge_aware_numeric_point_strategy
from .memory import process_rss_kib


@dataclass(frozen=True)
class NumericProperty:
    name: str
    bounds: list[tuple[float, float]]
    description: str
    failure: Callable[[np.ndarray], np.ndarray]


@dataclass
class PropertyBenchmarkResult:
    method: str
    property_name: str
    budget: int
    failures: int
    first_failure_index: int
    runtime_seconds: float
    process_rss_kib: float


def numeric_properties() -> list[NumericProperty]:
    """Return a small battery of floating-point properties with known traps."""

    def sqrt_square(points: np.ndarray) -> np.ndarray:
        x = points[:, 0]
        with np.errstate(over="ignore", invalid="ignore"):
            y = np.sqrt(x * x)
        rel = np.abs(y - np.abs(x)) / np.maximum(1.0, np.abs(x))
        return (~np.isfinite(y)) | (rel > 1e-10)

    def exp_log(points: np.ndarray) -> np.ndarray:
        x = points[:, 0]
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            y = np.log(np.exp(x))
        return (~np.isfinite(y)) | (np.abs(y - x) > 1e-9)

    def tan_period(points: np.ndarray) -> np.ndarray:
        x = points[:, 0]
        with np.errstate(over="ignore", invalid="ignore"):
            a = np.tan(x)
            b = np.tan(x + np.pi)
        scale = np.maximum(1.0, np.maximum(np.abs(a), np.abs(b)))
        return (~np.isfinite(a)) | (~np.isfinite(b)) | (np.abs(a - b) / scale > 1e-8)

    def division_roundtrip(points: np.ndarray) -> np.ndarray:
        x = points[:, 0]
        y = points[:, 1]
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            z = (x / y) * y
        rel = np.abs(z - x) / np.maximum(1.0, np.abs(x))
        return (y == 0.0) | (~np.isfinite(z)) | (rel > 1e-8)

    def matrix_solve(points: np.ndarray) -> np.ndarray:
        x = points[:, 0]
        y = points[:, 1]
        det = x * x - y * y
        cond_proxy = (np.abs(x) + np.abs(y)) / np.maximum(np.abs(x - y), 1e-300)
        return (np.abs(det) < 1e-8) | (cond_proxy > 1e12)

    return [
        NumericProperty("sqrt_square_overflow", [(-1e155, 1e155)], "sqrt(x*x) should remain close to abs(x)", sqrt_square),
        NumericProperty("exp_log_roundtrip", [(-800.0, 800.0)], "log(exp(x)) should remain close to x inside the finite range", exp_log),
        NumericProperty("tan_periodicity", [(-1e6, 1e6)], "tan(x + pi) should match tan(x) away from unstable points", tan_period),
        NumericProperty("division_roundtrip", [(-1e155, 1e155), (-1e155, 1e155)], "(x / y) * y should recover x away from zero/overflow", division_roundtrip),
        NumericProperty("symmetric_matrix_singularity", [(-1e6, 1e6), (-1e6, 1e6)], "2x2 symmetric systems fail near x=+/-y", matrix_solve),
    ]


def run(output_dir: Path, budget: int = 512, seeds: int = 5) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for seed in range(seeds):
        for prop in numeric_properties():
            for result in _run_property(prop, budget=budget, seed=seed):
                rows.append({"seed": seed, **asdict(result)})
    summary = _summarize(rows)
    payload = {"benchmark": "cover_property", "budget": budget, "seeds": seeds, "rows": rows, "summary": summary}
    (output_dir / "cover_property_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_csv(output_dir / "cover_property_summary.csv", rows)
    (output_dir / "COVER_PROPERTY_RESULT_CARD.md").write_text(_render_markdown(summary), encoding="utf-8")
    return payload


def _run_property(prop: NumericProperty, budget: int, seed: int) -> list[PropertyBenchmarkResult]:
    methods: dict[str, Callable[[list[tuple[float, float]], int, int], np.ndarray]] = {
        "random_uniform": random_uniform_cover,
        "sobol": sobol_cover,
        "halton": halton_cover,
        "latin_hypercube": latin_hypercube_cover,
        "powers_only": powers_only_cover,
        "boundary_only": boundary_only_cover,
        "rdt_cover": lambda bounds, budget, seed: rdt_cover(bounds, budget, seed=seed),
        "rdt_hybrid_cover": rdt_hybrid_cover,
    }
    results = []
    for name, generator in methods.items():
        start = perf_counter()
        points = generator(prop.bounds, budget, seed)
        failures = prop.failure(points)
        runtime = perf_counter() - start
        first = int(np.flatnonzero(failures)[0] + 1) if np.any(failures) else -1
        results.append(PropertyBenchmarkResult(name, prop.name, budget, int(np.count_nonzero(failures)), first, runtime, process_rss_kib()))
    results.append(_hypothesis_find(prop, budget=budget))
    return results


def _hypothesis_find(prop: NumericProperty, budget: int) -> PropertyBenchmarkResult:
    start = perf_counter()
    try:
        from hypothesis import find, settings  # type: ignore
        from hypothesis.errors import NoSuchExample  # type: ignore
    except ImportError:
        runtime = perf_counter() - start
        return PropertyBenchmarkResult("hypothesis_find", prop.name, budget, 0, -1, runtime, process_rss_kib())

    try:
        strategy = edge_aware_numeric_point_strategy(prop.bounds)

        def predicate(point: tuple[float, ...]) -> bool:
            return bool(prop.failure(np.asarray([point], dtype=float))[0])

        find(strategy, predicate, settings=settings(database=None, deadline=None, max_examples=budget, derandomize=True))
        failures = 1
        first = 1
    except NoSuchExample:
        failures = 0
        first = -1
    runtime = perf_counter() - start
    return PropertyBenchmarkResult("hypothesis_find", prop.name, budget, failures, first, runtime, process_rss_kib())


def _summarize(rows: list[dict]) -> list[dict]:
    summary = []
    for prop in sorted({row["property_name"] for row in rows}):
        for method in sorted({row["method"] for row in rows}):
            group = [row for row in rows if row["property_name"] == prop and row["method"] == method]
            if not group:
                continue
            found = [1.0 if row["failures"] > 0 else 0.0 for row in group]
            summary.append({
                "property_name": prop,
                "method": method,
                "runs": len(group),
                "found_rate": float(np.mean(found)),
                "failures_mean": float(np.mean([row["failures"] for row in group])),
                "first_failure_index_mean": float(np.mean([row["first_failure_index"] for row in group if row["first_failure_index"] > 0])) if any(row["first_failure_index"] > 0 for row in group) else -1.0,
                "runtime_seconds_mean": float(np.mean([row["runtime_seconds"] for row in group])),
                "process_rss_kib_max": float(max(row["process_rss_kib"] for row in group)),
            })
    return summary


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _render_markdown(summary: list[dict]) -> str:
    lines = [
        "# RDT-Cover Property Benchmark",
        "",
        "This is not the seeded edge-class corpus. It evaluates ordinary floating-point properties and includes a targeted Hypothesis `find` baseline.",
        "",
        "| Property | Best found-rate method | RDT found rate | Powers-only found rate | Hypothesis found rate |",
        "|---|---|---:|---:|---:|",
    ]
    for prop in sorted({row["property_name"] for row in summary}):
        group = [row for row in summary if row["property_name"] == prop]
        best = max(group, key=lambda row: (row["found_rate"], row["failures_mean"]))
        lookup = {row["method"]: row for row in group}
        lines.append(
            f"| {prop} | `{best['method']}` | "
            f"{lookup.get('rdt_cover', {}).get('found_rate', 0.0):.2f} | "
            f"{lookup.get('powers_only', {}).get('found_rate', 0.0):.2f} | "
            f"{lookup.get('hypothesis_find', {}).get('found_rate', 0.0):.2f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RDT-cover numeric property benchmark.")
    parser.add_argument("--output-dir", default="results/tmp/cover_property")
    parser.add_argument("--budget", type=int, default=512)
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    run(Path(args.output_dir), budget=args.budget, seeds=args.seeds)
    print(f"Wrote cover property benchmark results to {args.output_dir}")


if __name__ == "__main__":
    main()
