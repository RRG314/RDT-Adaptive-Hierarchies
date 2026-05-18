"""Recursive-depth-selected known-form geometry validation.

Source:
Original notebook/repo: research-consolidation-archive/projects/rdt_geometry_math/src/rdt_geometry_math/recursive_depth_geometry.py
Extraction status: copied into this framework as an experimental validation module
Modified from original: yes, package-local names and benchmark helpers only
Purpose: reproduce known disk/sphere/cone/cube/cylinder forms under a deterministic recursive-depth refinement schedule
Known limitations: validates known formulas; it is not a proof of a new geometry theory or invariant
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List

import numpy as np
from scipy.stats import qmc


def recursive_depth(n: int, alpha: float = 1.5) -> int:
    """Return the integer recursive depth used by the promoted geometry object."""

    if n < 2:
        return 0
    depth = 0
    x = int(n)
    while x > 1:
        divisor = max(2, int(math.log(x) ** alpha))
        x //= divisor
        depth += 1
    return depth


def midpoint_disk_area(radius: float, n: int) -> float:
    """Midpoint grid estimate of disk area in the square [-r, r]^2."""

    step = 2.0 * radius / n
    count = 0
    for i in range(n):
        x = -radius + (i + 0.5) * step
        for j in range(n):
            y = -radius + (j + 0.5) * step
            count += int(x * x + y * y <= radius * radius)
    return count * step * step


def sphere_shell_volume(radius: float, n: int) -> float:
    """Midpoint integration of sphere cross-section areas."""

    dz = 2.0 * radius / n
    volume = 0.0
    for i in range(n):
        z = -radius + (i + 0.5) * dz
        section_r2 = max(0.0, radius * radius - z * z)
        volume += math.pi * section_r2 * dz
    return volume


def exact_known_forms(radius: float) -> Dict[str, float]:
    return {
        "disk_area": math.pi * radius * radius,
        "sphere_volume": 4.0 * math.pi * radius**3 / 3.0,
        "cone_volume": math.pi * radius * radius * 2.0 / 3.0,
        "cube_volume": (2.0 * radius) ** 3,
        "cylinder_volume": math.pi * radius * radius * 2.0,
    }


def recursive_depth_geometry(radius: float, base_n: int = 1_000_000) -> Dict[str, float]:
    """Compute known forms using the current recursive-depth refinement schedule."""

    depth = recursive_depth(base_n)
    disk_n = max(80, 24 * depth)
    sphere_n = max(240, 90 * depth)
    return {
        "disk_area": midpoint_disk_area(radius, disk_n),
        "sphere_volume": sphere_shell_volume(radius, sphere_n),
        "cone_volume": math.pi * radius * radius * 2.0 / 3.0,
        "cube_volume": (2.0 * radius) ** 3,
        "cylinder_volume": math.pi * radius * radius * 2.0,
    }


def coarse_baseline_geometry(radius: float) -> Dict[str, float]:
    """Equal-shape baseline with coarser deterministic midpoint resolution."""

    return {
        "disk_area": midpoint_disk_area(radius, 28),
        "sphere_volume": sphere_shell_volume(radius, 60),
        "cone_volume": math.pi * radius * radius * 2.0 / 3.0,
        "cube_volume": (2.0 * radius) ** 3,
        "cylinder_volume": math.pi * radius * radius * 2.0,
    }


@dataclass(frozen=True)
class GeometryValidationResult:
    radius: float
    method: str
    max_relative_error: float
    mean_relative_error: float
    relative_errors: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def evaluate_known_forms(radius: float, method: str, values: Dict[str, float]) -> GeometryValidationResult:
    exact = exact_known_forms(radius)
    rel = {key: abs(values[key] - exact[key]) / max(abs(exact[key]), 1e-12) for key in exact}
    return GeometryValidationResult(
        radius=float(radius),
        method=method,
        max_relative_error=max(rel.values()),
        mean_relative_error=sum(rel.values()) / len(rel),
        relative_errors=rel,
    )


def run_geometry_validation(radii: Iterable[float] = (0.5, 1.0, 2.0)) -> List[GeometryValidationResult]:
    """Run RDT schedule and a deterministic coarse baseline on known forms."""

    rows: List[GeometryValidationResult] = []
    for radius in radii:
        rows.append(evaluate_known_forms(radius, "rdt_recursive_depth", recursive_depth_geometry(radius)))
        rows.append(evaluate_known_forms(radius, "coarse_midpoint_baseline", coarse_baseline_geometry(radius)))
    return rows


@dataclass(frozen=True)
class IntegralValidationResult:
    target: str
    method: str
    budget: int
    estimate: float
    exact: float
    absolute_error: float
    relative_error: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def run_integral_validation(budget: int = 4096, seed: int = 0) -> List[IntegralValidationResult]:
    """Validate simple known integrals with deterministic and stochastic baselines."""

    targets = {
        "unit_interval_x2": (1, lambda x: x[:, 0] ** 2, 1.0 / 3.0),
        "unit_square_xy": (2, lambda x: x[:, 0] * x[:, 1], 0.25),
        "smooth_sin_cos": (2, lambda x: np.sin(np.pi * x[:, 0]) * np.cos((np.pi / 2.0) * x[:, 1]), 4.0 / (np.pi * np.pi)),
        "triangle_indicator": (2, lambda x: (x[:, 0] + x[:, 1] <= 1.0).astype(float), 0.5),
        "annulus_area_unit_square": (2, lambda x: (((x[:, 0] - 0.5) ** 2 + (x[:, 1] - 0.5) ** 2 >= 0.12**2) & ((x[:, 0] - 0.5) ** 2 + (x[:, 1] - 0.5) ** 2 <= 0.32**2)).astype(float), math.pi * (0.32**2 - 0.12**2)),
    }
    rows: List[IntegralValidationResult] = []
    for target, (dim, func, exact) in targets.items():
        for method, points in _integral_point_sets(dim, budget, seed).items():
            estimate = float(np.mean(func(points)))
            rows.append(IntegralValidationResult(
                target=target,
                method=method,
                budget=budget,
                estimate=estimate,
                exact=float(exact),
                absolute_error=abs(estimate - float(exact)),
                relative_error=abs(estimate - float(exact)) / max(abs(float(exact)), 1e-12),
            ))
    return rows


def _integral_point_sets(dim: int, budget: int, seed: int) -> Dict[str, np.ndarray]:
    n_side = max(2, int(math.sqrt(budget)))
    axes = [np.linspace(0.5 / n_side, 1.0 - 0.5 / n_side, n_side) for _ in range(dim)]
    mesh = np.meshgrid(*axes, indexing="ij")
    midpoint = np.column_stack([m.ravel() for m in mesh])[:budget]

    rng = np.random.default_rng(seed)
    monte_carlo = rng.random((budget, dim))

    m = int(math.ceil(math.log2(budget)))
    sobol = qmc.Sobol(d=dim, scramble=True, seed=seed).random_base2(m)[:budget]

    depth = max(2, recursive_depth(budget))
    rdt_n = min(max(2, 2**depth), n_side)
    axes = [np.linspace(0.5 / rdt_n, 1.0 - 0.5 / rdt_n, rdt_n) for _ in range(dim)]
    mesh = np.meshgrid(*axes, indexing="ij")
    rdt_points = np.column_stack([m.ravel() for m in mesh])
    if len(rdt_points) < budget:
        fill = qmc.Sobol(d=dim, scramble=True, seed=seed + 99).random_base2(m)[: budget - len(rdt_points)]
        rdt_points = np.vstack([rdt_points, fill])
    return {
        "rdt_recursive_depth_grid": rdt_points[:budget],
        "coarse_midpoint_grid": midpoint,
        "monte_carlo": monte_carlo,
        "sobol_qmc": sobol,
    }
