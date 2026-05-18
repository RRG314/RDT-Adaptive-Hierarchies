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


def halton_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """Generate a scrambled Halton sequence over the numeric bounds."""

    dim = len(bounds)
    sampler = qmc.Halton(d=dim, scramble=True, seed=seed)
    sample = sampler.random(budget)
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


def boundary_only_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """Ablation baseline using boundaries, corners, and deterministic fill."""

    dim = len(bounds)
    center = np.array([(a + b) / 2 for a, b in bounds], dtype=float)
    candidates: list[np.ndarray] = [center]
    for d, (low, high) in enumerate(bounds):
        for value in (low, high):
            p = center.copy()
            p[d] = value
            candidates.append(p)
    for mask in range(min(2**dim, 256)):
        p = center.copy()
        for d, (low, high) in enumerate(bounds):
            p[d] = high if (mask >> d) & 1 else low
        candidates.append(p)
    return _dedupe_and_fill(candidates, bounds, budget, seed)


def midpoint_only_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """Ablation baseline using recursive midpoints but no shell jitter."""

    center = np.array([(a + b) / 2 for a, b in bounds], dtype=float)
    candidates: list[np.ndarray] = [center]
    depth = max(2, int(np.ceil(np.log2(max(2, budget // max(1, len(bounds)))))))
    for d, (low, high) in enumerate(bounds):
        for value in _recursive_midpoints(low, high, depth=depth):
            p = center.copy()
            p[d] = value
            candidates.append(p)
    return _dedupe_and_fill(candidates, bounds, budget, seed)


def powers_only_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """Ablation baseline using powers of ten and two plus zero where valid."""

    center = np.array([(a + b) / 2 for a, b in bounds], dtype=float)
    candidates: list[np.ndarray] = [center]
    for d, (low, high) in enumerate(bounds):
        anchors = [0.0] if low <= 0 <= high else []
        for e in range(-12, 13):
            anchors.extend([10.0**e, -(10.0**e), 2.0**e, -(2.0**e)])
        for value in sorted(set(anchors)):
            if low <= value <= high:
                p = center.copy()
                p[d] = value
                candidates.append(p)
    return _dedupe_and_fill(candidates, bounds, budget, seed)


def hypothesis_cover(bounds: List[Tuple[float, float]], budget: int, seed: int = 0) -> np.ndarray:
    """Generate coverage points using Hypothesis strategies.

    This is a real property-based-testing integration. It builds a Hypothesis
    strategy over the numeric domain, uses ``hypothesis.find`` to search for
    the same seeded edge-case predicates used by the benchmark, and fills the
    remaining budget with deterministic examples from the same strategy family.

    The method is intentionally named as a targeted baseline: it has access to
    the benchmark predicates, which is stronger than blind random/Sobol
    sampling and should not be presented as an ordinary black-box sampler.
    """

    try:
        from hypothesis import HealthCheck, Phase, find, settings, strategies as st  # type: ignore
        from hypothesis.errors import NoSuchExample  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("hypothesis_cover requires the optional hypothesis package") from exc

    dim = len(bounds)
    rng = np.random.default_rng(seed)

    finite_bounds = [(float(a), float(b)) for a, b in bounds]
    anchors_by_dim: list[list[float]] = []
    for low, high in finite_bounds:
        anchors = [low, high, (low + high) / 2.0]
        if low <= 0 <= high:
            anchors.append(0.0)
        max_abs = max(abs(low), abs(high), 1e-12)
        for e in range(-12, int(np.ceil(np.log10(max_abs))) + 1):
            for sign in (-1.0, 1.0):
                val = sign * (10.0 ** e)
                if low <= val <= high:
                    anchors.append(val)
            for sign in (-1.0, 1.0):
                val = sign * (2.0 ** e)
                if low <= val <= high:
                    anchors.append(val)
        anchors_by_dim.append(sorted(set(float(v) for v in anchors)))

    @st.composite
    def point_strategy(draw):
        mode = draw(st.integers(min_value=0, max_value=5))
        values = [
            draw(st.floats(min_value=low, max_value=high, allow_nan=False, allow_infinity=False, width=64))
            for low, high in finite_bounds
        ]
        if mode == 1 and dim >= 1:
            values[0] = 0.0 if finite_bounds[0][0] <= 0 <= finite_bounds[0][1] else finite_bounds[0][0]
        elif mode == 2 and dim >= 1:
            values[0] = draw(st.sampled_from(anchors_by_dim[0]))
        elif mode == 3 and dim >= 2:
            magnitude = draw(st.sampled_from([1e3, 1e4, 1e5, 1e6]))
            sign = draw(st.sampled_from([-1.0, 1.0]))
            values[0] = float(np.clip(sign * magnitude, finite_bounds[0][0], finite_bounds[0][1]))
            values[1] = float(np.clip(-values[0], finite_bounds[1][0], finite_bounds[1][1]))
        elif mode == 4:
            values = [high if draw(st.booleans()) else low for low, high in finite_bounds]
        elif mode == 5 and dim >= 2:
            angle = draw(st.floats(min_value=0.0, max_value=float(2 * np.pi), allow_nan=False, allow_infinity=False))
            values[0] = float(np.clip(np.cos(angle), finite_bounds[0][0], finite_bounds[0][1]))
            values[1] = float(np.clip(np.sin(angle), finite_bounds[1][0], finite_bounds[1][1]))
        return tuple(float(v) for v in values)

    strategy = point_strategy()
    hyp_settings = settings(
        max_examples=max(256, budget),
        derandomize=True,
        database=None,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow],
        phases=[Phase.generate, Phase.shrink],
    )

    def as_array(point: tuple[float, ...]) -> np.ndarray:
        return np.asarray(point, dtype=float)

    scalar_predicates = {
        "zero_boundary": lambda p: abs(p[0]) < 1e-9,
        "large_cancellation": lambda p: dim >= 2 and abs(p[0] + p[1]) < 1e-6 and max(abs(p[0]), abs(p[1])) > 1e3,
        "power_transition": lambda p: _is_power_transition(p[0]),
        "outer_corner": lambda p: all(abs(v) >= 0.95 * max(abs(low), abs(high)) for v, (low, high) in zip(p, finite_bounds)),
        "thin_annulus": lambda p: dim >= 2 and abs((p[0] ** 2 + p[1] ** 2) ** 0.5 - 1.0) < 0.015,
    }

    candidates: list[np.ndarray] = []
    for predicate in scalar_predicates.values():
        try:
            candidates.append(as_array(find(strategy, predicate, settings=hyp_settings)))
        except NoSuchExample:
            continue

    # Deterministically fill the remaining budget with examples that come from
    # the same edge-aware strategy family. Calling .example() is deliberately
    # avoided here; we construct the fill points ourselves from the strategy's
    # explicit modes so benchmark output remains quiet and reproducible.
    candidates.extend(_hypothesis_style_fill(finite_bounds, anchors_by_dim, max(0, budget - len(candidates)), rng))
    arr = np.unique(np.round(np.vstack(candidates), decimals=14), axis=0) if candidates else np.empty((0, dim))
    if len(arr) >= budget:
        return arr[:budget]
    extra = random_uniform_cover(bounds, budget - len(arr), seed=seed + 77_777)
    return np.vstack([arr, extra])


def _is_power_transition(value: float) -> bool:
    with np.errstate(divide="ignore", invalid="ignore"):
        log_abs = np.log10(max(abs(float(value)), 1e-300))
    return bool(np.min(np.abs(log_abs - np.arange(-9, 10))) < 0.015)


def _hypothesis_style_fill(
    bounds: list[tuple[float, float]],
    anchors_by_dim: list[list[float]],
    count: int,
    rng: np.random.Generator,
) -> list[np.ndarray]:
    if count <= 0:
        return []
    dim = len(bounds)
    candidates: list[np.ndarray] = []
    for i in range(count):
        mode = i % 6
        values = np.array([rng.uniform(low, high) for low, high in bounds], dtype=float)
        if mode == 1 and dim >= 1:
            values[0] = 0.0 if bounds[0][0] <= 0 <= bounds[0][1] else bounds[0][0]
        elif mode == 2 and dim >= 1:
            values[0] = anchors_by_dim[0][i % len(anchors_by_dim[0])]
        elif mode == 3 and dim >= 2:
            magnitude = [1e3, 1e4, 1e5, 1e6][i % 4]
            sign = -1.0 if (i // 4) % 2 else 1.0
            values[0] = np.clip(sign * magnitude, bounds[0][0], bounds[0][1])
            values[1] = np.clip(-values[0], bounds[1][0], bounds[1][1])
        elif mode == 4:
            values = np.array([high if ((i + d) % 2) else low for d, (low, high) in enumerate(bounds)], dtype=float)
        elif mode == 5 and dim >= 2:
            angle = 2 * np.pi * ((i * 0.61803398875) % 1.0)
            values[0] = np.clip(np.cos(angle), bounds[0][0], bounds[0][1])
            values[1] = np.clip(np.sin(angle), bounds[1][0], bounds[1][1])
        candidates.append(values)
    return candidates


def _dedupe_and_fill(
    candidates: list[np.ndarray],
    bounds: List[Tuple[float, float]],
    budget: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.unique(np.round(np.vstack(candidates), decimals=14), axis=0) if candidates else np.empty((0, len(bounds)))
    if len(arr) >= budget:
        return arr[:budget]
    extra = rng.uniform([a for a, _ in bounds], [b for _, b in bounds], size=(budget - len(arr), len(bounds)))
    return np.vstack([arr, extra])


def seeded_numeric_bug_predicates(points: np.ndarray) -> Dict[str, np.ndarray]:
    x = np.asarray(points, dtype=float)
    first = x[:, 0]
    second = x[:, 1] if x.shape[1] > 1 else x[:, 0]
    radius = np.linalg.norm(x, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_abs = np.log10(np.maximum(np.abs(first), 1e-300))
    near_power_ten = np.min(np.abs(log_abs[:, None] - np.arange(-12, 13)[None, :]), axis=1) < 0.015
    with np.errstate(divide="ignore", invalid="ignore"):
        log2_abs = np.log2(np.maximum(np.abs(first), 1e-300))
    near_power_two = np.min(np.abs(log2_abs[:, None] - np.arange(-40, 41)[None, :]), axis=1) < 0.02
    smallest = np.minimum(np.abs(first), np.abs(second))
    largest = np.maximum(np.abs(first), np.abs(second))
    condition_ratio = np.divide(largest, smallest, out=np.zeros_like(largest), where=smallest > 0)
    return {
        "zero_boundary": np.abs(first) < 1e-9,
        "near_zero_division": (np.abs(second) > 0) & (np.abs(second) < 1e-6),
        "overflow_adjacent": np.any(np.abs(x) > 9e5, axis=1),
        "underflow_adjacent": (np.abs(first) > 0) & (np.abs(first) < 1e-9),
        "large_cancellation": (np.abs(first + second) < 1e-6) & (np.maximum(np.abs(first), np.abs(second)) > 1e3),
        "power_of_ten_transition": near_power_ten,
        "power_of_two_transition": near_power_two,
        "sqrt_boundary": (first >= 0) & (first < 1e-6),
        "log_domain_boundary": (first > 0) & (first < 1e-6),
        "trigonometric_periodic_boundary": np.min(
            np.abs((first[:, None] / (np.pi / 2.0)) - np.arange(-8, 9)[None, :]), axis=1
        ) < 0.015,
        "outer_corner": np.all(np.abs(x) > 0.95 * np.max(np.abs(x), axis=0), axis=1),
        "thin_annulus": np.abs(radius - 1.0) < 0.015,
        "near_singular_symmetric_2x2": (np.abs(first - second) < 1e-6) & (largest > 1.0),
        "ill_conditioned_vector": condition_ratio > 1e9,
    }


@dataclass
class CoverBenchmarkResult:
    method: str
    budget: int
    discovered_bug_classes: int
    total_hits: int
    first_hit_index: int
    hit_rate: float
    min_pairwise_distance: float
    centered_discrepancy: float
    runtime_seconds: float


def benchmark_cover_methods(bounds: List[Tuple[float, float]], budget: int = 512, seed: int = 0) -> Dict[str, CoverBenchmarkResult]:
    methods: Dict[str, Callable[[List[Tuple[float, float]], int, int], np.ndarray]] = {
        "rdt_cover": lambda b, n, s: rdt_cover(b, n, seed=s),
        "rdt_hybrid_cover": rdt_hybrid_cover,
        "boundary_only": boundary_only_cover,
        "midpoint_only": midpoint_only_cover,
        "powers_only": powers_only_cover,
        "random_uniform": random_uniform_cover,
        "sobol": sobol_cover,
        "halton": halton_cover,
        "latin_hypercube": latin_hypercube_cover,
    }
    try:
        import hypothesis  # type: ignore  # noqa: F401
    except ImportError:
        pass
    else:
        methods["hypothesis_targeted"] = hypothesis_cover
    results = {}
    for name, func in methods.items():
        start = perf_counter()
        pts = func(bounds, budget, seed)
        elapsed = perf_counter() - start
        bugs = seeded_numeric_bug_predicates(pts)
        discovered = sum(bool(np.any(mask)) for mask in bugs.values())
        hits = int(sum(np.sum(mask) for mask in bugs.values()))
        any_hit = np.zeros(len(pts), dtype=bool)
        for mask in bugs.values():
            any_hit |= mask
        first_hit_index = int(np.argmax(any_hit) + 1) if bool(np.any(any_hit)) else -1
        hit_rate = float(hits / max(1, len(pts) * len(bugs)))
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
        results[name] = CoverBenchmarkResult(name, budget, discovered, hits, first_hit_index, hit_rate, min_dist, discrepancy, elapsed)
    return results


def _normalize_to_unit(points: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
    lows = np.array([a for a, _ in bounds], dtype=float)
    highs = np.array([b for _, b in bounds], dtype=float)
    return np.clip((points - lows) / np.maximum(highs - lows, 1e-12), 0, 1)
