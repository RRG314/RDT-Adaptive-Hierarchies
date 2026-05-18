from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np
from scipy.stats import qmc


def _recursive_midpoints(low: float, high: float, depth: int) -> List[float]:
    points = []
    intervals = [(float(low), float(high))]
    for _ in range(depth):
        new_intervals = []
        for a, b in intervals:
            m = (a + b) / 2.0
            points.append(m)
            new_intervals.append((a, m))
            new_intervals.append((m, b))
        intervals = new_intervals
    return points


def rdt_cover(bounds: List[Tuple[float, float]], budget: int, shells: int = 12, seed: int = 0) -> np.ndarray:
    """Generate deterministic multi-scale numeric coverage points.

    The generator emphasizes boundaries, zero, powers of ten, recursive
    midpoints, and shell radii. It is intended for numerical validation, not
    random sampling.
    """

    rng = np.random.default_rng(seed)
    dim = len(bounds)
    candidates: List[np.ndarray] = []
    center = np.array([(a + b) / 2 for a, b in bounds], dtype=float)
    candidates.append(center)

    for d, (low, high) in enumerate(bounds):
        anchors = [low, high, (low + high) / 2.0]
        if low <= 0 <= high:
            anchors.append(0.0)
        max_abs = max(abs(low), abs(high), 1e-12)
        min_exp = int(np.floor(np.log10(max(1e-12, max_abs))) - shells // 2)
        max_exp = int(np.ceil(np.log10(max_abs)))
        for e in range(min_exp, max_exp + 1):
            val = 10.0 ** e
            anchors.extend([val, -val])
        anchors.extend(_recursive_midpoints(low, high, depth=max(1, int(np.ceil(np.log2(shells))))))
        for anchor in anchors:
            if low <= anchor <= high:
                p = center.copy()
                p[d] = anchor
                candidates.append(p)

    # Cross-dimensional corners and shell combinations.
    for mask in range(1, min(2 ** dim, 256)):
        p = center.copy()
        for d, (low, high) in enumerate(bounds):
            p[d] = high if (mask >> d) & 1 else low
        candidates.append(p)

    # Deterministic shell jitter fills the remaining budget.
    while len(candidates) < budget:
        p = center.copy()
        radius_scale = 10.0 ** rng.uniform(-shells / 3, 0)
        direction = rng.normal(size=dim)
        norm = np.linalg.norm(direction)
        if norm == 0:
            continue
        direction /= norm
        spans = np.array([(b - a) / 2 for a, b in bounds], dtype=float)
        p = center + direction * spans * radius_scale
        for d, (low, high) in enumerate(bounds):
            p[d] = np.clip(p[d], low, high)
        candidates.append(p)

    arr = np.unique(np.round(np.vstack(candidates), decimals=14), axis=0)
    if len(arr) >= budget:
        return arr[:budget]
    extra = rng.uniform([a for a, _ in bounds], [b for _, b in bounds], size=(budget - len(arr), dim))
    return np.vstack([arr, extra])


def rdt_hybrid_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """RDT edge/shell cases plus Sobol fill for better space coverage."""

    edge_budget = max(1, budget // 2)
    shell = rdt_cover(bounds, edge_budget, seed=seed)
    sobol = sobol_cover(bounds, budget - edge_budget + 32, seed=seed + 10_000)
    arr = np.unique(np.round(np.vstack([shell, sobol]), decimals=14), axis=0)
    if len(arr) >= budget:
        return arr[:budget]
    extra = random_uniform_cover(bounds, budget - len(arr), seed=seed + 20_000)
    return np.vstack([arr, extra])


def random_uniform_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform([a for a, _ in bounds], [b for _, b in bounds], size=(budget, len(bounds)))


def sobol_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    dim = len(bounds)
    sampler = qmc.Sobol(d=dim, scramble=True, seed=seed)
    m = int(np.ceil(np.log2(budget)))
    sample = sampler.random_base2(m)[:budget]
    lows = np.array([a for a, _ in bounds], dtype=float)
    highs = np.array([b for _, b in bounds], dtype=float)
    return lows + sample * (highs - lows)


def latin_hypercube_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    dim = len(bounds)
    sampler = qmc.LatinHypercube(d=dim, seed=seed)
    sample = sampler.random(budget)
    lows = np.array([a for a, _ in bounds], dtype=float)
    highs = np.array([b for _, b in bounds], dtype=float)
    return lows + sample * (highs - lows)


def seeded_numeric_bug_predicates(points: np.ndarray) -> Dict[str, np.ndarray]:
    x = np.asarray(points, dtype=float)
    first = x[:, 0]
    second = x[:, 1] if x.shape[1] > 1 else x[:, 0]
    radius = np.linalg.norm(x, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_abs = np.log10(np.maximum(np.abs(first), 1e-300))
    near_power = np.min(np.abs(log_abs[:, None] - np.arange(-9, 10)[None, :]), axis=1) < 0.015
    return {
        "zero_boundary": np.abs(first) < 1e-9,
        "large_cancellation": (np.abs(first + second) < 1e-6) & (np.maximum(np.abs(first), np.abs(second)) > 1e3),
        "power_transition": near_power,
        "outer_corner": np.all(np.abs(x) > 0.95 * np.max(np.abs(x), axis=0), axis=1),
        "thin_annulus": np.abs(radius - 1.0) < 0.015,
    }


@dataclass
class CoverBenchmarkResult:
    method: str
    budget: int
    discovered_bug_classes: int
    total_hits: int
    min_pairwise_distance: float
    centered_discrepancy: float
    runtime_seconds: float


def benchmark_cover_methods(bounds: List[Tuple[float, float]], budget: int = 512, seed: int = 0) -> Dict[str, CoverBenchmarkResult]:
    methods: Dict[str, Callable[[List[Tuple[float, float]], int, int], np.ndarray]] = {
        "rdt_cover": lambda b, n, s: rdt_cover(b, n, seed=s),
        "rdt_hybrid_cover": rdt_hybrid_cover,
        "random_uniform": random_uniform_cover,
        "sobol": sobol_cover,
        "latin_hypercube": latin_hypercube_cover,
    }
    results = {}
    for name, func in methods.items():
        start = perf_counter()
        pts = func(bounds, budget, seed)
        elapsed = perf_counter() - start
        bugs = seeded_numeric_bug_predicates(pts)
        discovered = sum(bool(np.any(mask)) for mask in bugs.values())
        hits = int(sum(np.sum(mask) for mask in bugs.values()))
        sample = pts[: min(len(pts), 1000)]
        if len(sample) > 1:
            diffs = sample[:, None, :] - sample[None, :, :]
            dists = np.sqrt(np.sum(diffs * diffs, axis=2))
            dists[dists == 0] = np.inf
            min_dist = float(np.min(dists))
        else:
            min_dist = 0.0
        norm = _normalize_to_unit(pts, bounds)
        discrepancy = float(qmc.discrepancy(norm, method="CD")) if len(norm) else float("nan")
        results[name] = CoverBenchmarkResult(name, budget, discovered, hits, min_dist, discrepancy, elapsed)
    return results


def _normalize_to_unit(points: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
    lows = np.array([a for a, _ in bounds], dtype=float)
    highs = np.array([b for _, b in bounds], dtype=float)
    return np.clip((points - lows) / np.maximum(highs - lows, 1e-12), 0, 1)
