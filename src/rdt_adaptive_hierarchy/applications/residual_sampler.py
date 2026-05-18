from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Optional

import numpy as np

from ..core.hierarchy import RDTHierarchy


@dataclass
class SamplerResult:
    method: str
    field: str
    selected_count: int
    top_recall: float
    mean_residual: float
    coverage_entropy: float
    min_grid_coverage: float
    composite_score: float
    runtime_seconds: float


class RDTResidualSampler:
    """Hierarchical residual sampler with coverage pressure.

    It selects high-residual cells while reserving part of the budget for broad
    shell coverage. This is designed to avoid the over-concentration failure of
    greedy top-residual sampling.
    """

    def __init__(
        self,
        max_cells: int = 64,
        exploration_fraction: float = 0.25,
        residual_weight: float = 1.0,
        gradient_weight: float = 0.35,
        coverage_weight: float = 0.15,
        random_state: int = 0,
    ):
        self.max_cells = int(max_cells)
        self.exploration_fraction = float(exploration_fraction)
        self.residual_weight = float(residual_weight)
        self.gradient_weight = float(gradient_weight)
        self.coverage_weight = float(coverage_weight)
        self.rng = np.random.default_rng(random_state)

    def select(
        self,
        points: np.ndarray,
        residuals: np.ndarray,
        gradients: Optional[np.ndarray] = None,
        n_new: int = 256,
    ) -> np.ndarray:
        x = np.asarray(points, dtype=float)
        r = np.asarray(residuals, dtype=float)
        g = np.zeros_like(r) if gradients is None else np.asarray(gradients, dtype=float)
        if len(x) != len(r):
            raise ValueError("points and residuals must have same length")
        hierarchy = RDTHierarchy(max_leaves=min(self.max_cells, len(x)), min_leaf_size=max(4, len(x) // (self.max_cells * 4))).fit(x)
        cells = hierarchy.active_nodes(min(self.max_cells, len(hierarchy.split_sequence) + 1))
        cell_scores = []
        for node_id in cells:
            idx = hierarchy.nodes[node_id].indices
            if idx.size == 0:
                continue
            score = self.residual_weight * float(np.mean(r[idx])) + self.gradient_weight * float(np.mean(g[idx]))
            score += 0.05 * hierarchy.nodes[node_id].depth
            cell_scores.append((score, node_id, idx))
        cell_scores.sort(reverse=True, key=lambda t: t[0])

        selected = []
        exploit_budget = int(round(n_new * (1.0 - self.exploration_fraction)))
        for _, _, idx in cell_scores:
            if len(selected) >= exploit_budget:
                break
            take = max(1, min(len(idx), (exploit_budget - len(selected) + 1) // 2))
            order = idx[np.argsort(r[idx] + 0.25 * g[idx])[::-1]]
            selected.extend(order[:take].tolist())

        # Coverage pass: one representative from as many remaining cells as possible.
        used = set(selected)
        for _, _, idx in reversed(cell_scores):
            if len(selected) >= n_new:
                break
            candidates = [int(i) for i in idx if int(i) not in used]
            if not candidates:
                continue
            centroid = np.mean(x[candidates], axis=0)
            distances = np.sum((x[candidates] - centroid) ** 2, axis=1)
            chosen = candidates[int(np.argmin(distances))]
            selected.append(chosen)
            used.add(chosen)

        if len(selected) < n_new:
            remaining = np.array([i for i in range(len(x)) if i not in used], dtype=int)
            if remaining.size:
                extra = self.rng.choice(remaining, size=min(n_new - len(selected), remaining.size), replace=False)
                selected.extend(extra.tolist())
        return np.array(selected[:n_new], dtype=np.int64)


class RDTTunedResidualSampler:
    """Selects the best RDT sampler setting by an internal residual/coverage score."""

    def __init__(self, random_state: int = 0):
        self.random_state = int(random_state)

    def select(self, points: np.ndarray, residuals: np.ndarray, gradients: Optional[np.ndarray] = None, n_new: int = 256) -> np.ndarray:
        best_selected = None
        best_score = -np.inf
        for exploration in [0.05, 0.15, 0.25, 0.35]:
            for cells in [32, 64, 96]:
                sampler = RDTResidualSampler(max_cells=cells, exploration_fraction=exploration, random_state=self.random_state)
                selected = sampler.select(points, residuals, gradients, n_new=n_new)
                entropy, cover = _coverage_entropy(points, selected)
                score = float(np.mean(residuals[selected])) + 0.35 * entropy + 0.20 * cover
                if score > best_score:
                    best_score = score
                    best_selected = selected
        assert best_selected is not None
        return best_selected


def synthetic_residual_field(points: np.ndarray, name: str) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(points, dtype=float)
    px = x[:, 0]
    py = x[:, 1]
    if name == "sharp_front":
        front = np.exp(-((px - 0.52) ** 2) / 0.0015)
        boundary = 0.4 * np.exp(-(np.minimum.reduce([px, py, 1 - px, 1 - py]) ** 2) / 0.003)
        residual = front + boundary
        grad = np.abs(px - 0.52) * front / 0.0015 + boundary
    elif name == "two_hotspots":
        residual = np.exp(-80 * ((px - 0.25) ** 2 + (py - 0.75) ** 2))
        residual += 0.8 * np.exp(-120 * ((px - 0.72) ** 2 + (py - 0.32) ** 2))
        grad = residual * np.sqrt((px - 0.5) ** 2 + (py - 0.5) ** 2)
    elif name == "oscillatory":
        residual = 0.25 + np.abs(np.sin(18 * px) * np.cos(15 * py))
        residual += 0.6 * np.exp(-150 * ((px - 0.85) ** 2 + (py - 0.15) ** 2))
        grad = np.abs(18 * np.cos(18 * px) * np.cos(15 * py)) + residual
    elif name == "multi_front":
        front_a = np.exp(-((px - 0.28) ** 2) / 0.0012)
        front_b = np.exp(-((py - 0.68) ** 2) / 0.0018)
        diagonal = np.exp(-((px - py + 0.12) ** 2) / 0.0015)
        residual = 0.45 * front_a + 0.35 * front_b + 0.55 * diagonal
        grad = front_a + front_b + diagonal
    else:
        raise ValueError(f"unknown residual field {name!r}")
    residual = residual / max(float(np.max(residual)), 1e-12)
    grad = grad / max(float(np.max(grad)), 1e-12)
    return residual, grad


def _coverage_entropy(points: np.ndarray, selected: np.ndarray, bins: int = 8) -> tuple[float, float]:
    pts = points[selected]
    hist, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=bins, range=[[0, 1], [0, 1]])
    p = hist.ravel() / max(1, hist.sum())
    nz = p[p > 0]
    entropy = -float(np.sum(nz * np.log(nz))) / np.log(bins * bins)
    min_cover = float(np.mean(hist.ravel() > 0))
    return entropy, min_cover


def evaluate_selection(points: np.ndarray, residuals: np.ndarray, selected: np.ndarray, method: str, field: str, runtime: float) -> SamplerResult:
    n_top = max(1, int(0.05 * len(points)))
    top = set(np.argsort(residuals)[-n_top:].tolist())
    selected_set = set(selected.tolist())
    top_recall = len(top & selected_set) / n_top
    entropy, min_cover = _coverage_entropy(points, selected)
    mean_residual = float(np.mean(residuals[selected]))
    composite = 0.45 * top_recall + 0.35 * entropy + 0.20 * min_cover
    return SamplerResult(method, field, len(selected), top_recall, mean_residual, entropy, min_cover, composite, runtime)


def benchmark_residual_samplers(points: np.ndarray, field: str, n_new: int = 256, seed: int = 0) -> Dict[str, SamplerResult]:
    rng = np.random.default_rng(seed)
    residuals, gradients = synthetic_residual_field(points, field)
    results: Dict[str, SamplerResult] = {}

    start = perf_counter()
    selected = RDTResidualSampler(random_state=seed).select(points, residuals, gradients, n_new=n_new)
    results["rdt_residual"] = evaluate_selection(points, residuals, selected, "rdt_residual", field, perf_counter() - start)

    start = perf_counter()
    selected = RDTResidualSampler(coverage_weight=0.0, exploration_fraction=0.0, random_state=seed).select(points, residuals, gradients, n_new=n_new)
    results["rdt_no_coverage"] = evaluate_selection(points, residuals, selected, "rdt_no_coverage", field, perf_counter() - start)

    start = perf_counter()
    selected = RDTResidualSampler(gradient_weight=0.0, random_state=seed).select(points, residuals, None, n_new=n_new)
    results["rdt_no_gradient"] = evaluate_selection(points, residuals, selected, "rdt_no_gradient", field, perf_counter() - start)

    start = perf_counter()
    selected = RDTTunedResidualSampler(random_state=seed).select(points, residuals, gradients, n_new=n_new)
    results["rdt_residual_tuned"] = evaluate_selection(points, residuals, selected, "rdt_residual_tuned", field, perf_counter() - start)

    start = perf_counter()
    selected = rng.choice(len(points), size=n_new, replace=False)
    results["uniform"] = evaluate_selection(points, residuals, selected, "uniform", field, perf_counter() - start)

    start = perf_counter()
    selected = np.argsort(residuals)[-n_new:]
    results["top_residual"] = evaluate_selection(points, residuals, selected, "top_residual", field, perf_counter() - start)

    start = perf_counter()
    selected = np.argsort(residuals + 0.35 * gradients)[-n_new:]
    results["top_residual_gradient"] = evaluate_selection(points, residuals, selected, "top_residual_gradient", field, perf_counter() - start)

    start = perf_counter()
    weights = residuals + 1e-9
    weights = weights / weights.sum()
    selected = rng.choice(len(points), size=n_new, replace=False, p=weights)
    results["residual_proportional"] = evaluate_selection(points, residuals, selected, "residual_proportional", field, perf_counter() - start)

    start = perf_counter()
    selected = _stratified_residual(points, residuals, n_new=n_new, bins=8)
    results["grid_stratified_residual"] = evaluate_selection(points, residuals, selected, "grid_stratified_residual", field, perf_counter() - start)
    return results


def _stratified_residual(points: np.ndarray, residuals: np.ndarray, n_new: int, bins: int = 8) -> np.ndarray:
    x = np.asarray(points)
    cell_x = np.clip(np.floor(x[:, 0] * bins).astype(int), 0, bins - 1)
    cell_y = np.clip(np.floor(x[:, 1] * bins).astype(int), 0, bins - 1)
    cell = cell_y * bins + cell_x
    selected = []
    cell_scores = []
    for c in range(bins * bins):
        idx = np.where(cell == c)[0]
        if idx.size == 0:
            continue
        cell_scores.append((float(np.mean(residuals[idx])), idx))
    cell_scores.sort(reverse=True, key=lambda t: t[0])
    per_cell = max(1, n_new // max(1, len(cell_scores)))
    for _, idx in cell_scores:
        if len(selected) >= n_new:
            break
        order = idx[np.argsort(residuals[idx])[::-1]]
        selected.extend(order[:per_cell].tolist())
    if len(selected) < n_new:
        used = set(selected)
        order = np.argsort(residuals)[::-1]
        for i in order:
            if int(i) not in used:
                selected.append(int(i))
                if len(selected) >= n_new:
                    break
    return np.array(selected[:n_new], dtype=np.int64)
