from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Iterable, List

import numpy as np

from ..core.hierarchy import rdt_depth_int


def _js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / max(float(p.sum()), 1e-12)
    q = q / max(float(q.sum()), 1e-12)
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_pm = np.where(p > 0, p * np.log(p / np.maximum(m, 1e-12)), 0)
        kl_qm = np.where(q > 0, q * np.log(q / np.maximum(m, 1e-12)), 0)
    return float(0.5 * np.sum(kl_pm) + 0.5 * np.sum(kl_qm))


class RDTShellEntropySketch:
    """Rolling shell-distribution drift sketch for scalar streams."""

    def __init__(self, max_shell: int = 24, scale: float = 1_000.0, signed: bool = False, standardize: bool = True):
        self.max_shell = int(max_shell)
        self.scale = float(scale)
        self.signed = bool(signed)
        self.standardize = bool(standardize)
        self.center = 0.0
        self.unit = 1.0
        size = (2 * self.max_shell + 3) if self.signed else (self.max_shell + 1)
        self.reference = np.ones(size, dtype=float)
        self.current = np.ones(size, dtype=float)

    def shell_id(self, value: float) -> int:
        val = float(value)
        if self.standardize:
            val = (val - self.center) / max(self.unit, 1e-12)
        q = int(abs(val) * self.scale)
        depth = min(self.max_shell, rdt_depth_int(q))
        if not self.signed:
            return depth
        if abs(val) < 1e-15:
            return self.max_shell + 1
        return depth if val < 0 else self.max_shell + 2 + depth

    def fit_reference(self, values: Iterable[float]) -> "RDTShellEntropySketch":
        arr = np.asarray(list(values), dtype=float)
        if self.standardize and arr.size:
            self.center = float(np.median(arr))
            q25, q75 = np.percentile(arr, [25, 75])
            iqr_scale = float((q75 - q25) / 1.349) if q75 > q25 else 0.0
            self.unit = iqr_scale if iqr_scale > 1e-12 else float(np.std(arr) + 1e-12)
        self.reference = self._counts(arr) + 1.0
        return self

    def update_window(self, values: Iterable[float]) -> float:
        self.current = self._counts(values) + 1.0
        return self.drift_score()

    def drift_score(self) -> float:
        return _js_divergence(self.reference, self.current)

    def changed_shells(self, top_k: int = 3) -> List[int]:
        p = self.reference / self.reference.sum()
        q = self.current / self.current.sum()
        delta = np.abs(q - p)
        return np.argsort(delta)[-top_k:][::-1].astype(int).tolist()

    def _counts(self, values: Iterable[float]) -> np.ndarray:
        size = (2 * self.max_shell + 3) if self.signed else (self.max_shell + 1)
        counts = np.zeros(size, dtype=float)
        for value in values:
            counts[self.shell_id(float(value))] += 1.0
        return counts


@dataclass
class DriftBenchmarkResult:
    method: str
    scenario: str
    threshold: float
    false_positive_rate: float
    detection_delay: int
    detected: bool
    runtime_seconds: float


def _rolling_windows(stream: np.ndarray, window: int, step: int):
    for start in range(0, len(stream) - window + 1, step):
        yield start, stream[start:start + window]


def synthetic_stream(scenario: str, n: int = 4096, change: int = 2048, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    before = rng.normal(0, 1, size=change)
    after_n = n - change
    if scenario == "mean_shift":
        after = rng.normal(0.75, 1, size=after_n)
    elif scenario == "tail_shift":
        after = rng.standard_t(df=2, size=after_n)
    elif scenario == "variance_shift":
        after = rng.normal(0, 2.0, size=after_n)
    elif scenario == "scale_mixture":
        mask = rng.random(after_n) < 0.12
        after = rng.normal(0, 1, size=after_n)
        after[mask] += rng.normal(0, 8, size=np.sum(mask))
    else:
        raise ValueError(f"unknown scenario {scenario!r}")
    return np.concatenate([before, after])


def benchmark_drift_methods(scenario: str, seed: int = 0, window: int = 256, step: int = 32) -> Dict[str, DriftBenchmarkResult]:
    stream = synthetic_stream(scenario, seed=seed)
    change = len(stream) // 2
    reference = stream[:change]
    calib_scores: Dict[str, List[float]] = {"rdt_shell_js": [], "rdt_signed_shell_js": [], "histogram_js": [], "mean_std": [], "entropy_delta": []}

    sketch = RDTShellEntropySketch().fit_reference(reference)
    signed_sketch = RDTShellEntropySketch(signed=True).fit_reference(reference)
    ref_hist, edges = np.histogram(reference, bins=32, range=(-6, 6))
    ref_hist = ref_hist + 1
    ref_mean = float(np.mean(reference))
    ref_std = float(np.std(reference) + 1e-9)
    ref_entropy = _entropy(ref_hist)

    starts = []
    method_scores: Dict[str, List[float]] = {k: [] for k in calib_scores}
    start_time = perf_counter()
    for start, win in _rolling_windows(stream, window, step):
        starts.append(start)
        method_scores["rdt_shell_js"].append(sketch.update_window(win))
        method_scores["rdt_signed_shell_js"].append(signed_sketch.update_window(win))
        hist, _ = np.histogram(win, bins=edges)
        hist = hist + 1
        method_scores["histogram_js"].append(_js_divergence(ref_hist, hist))
        method_scores["mean_std"].append(abs(float(np.mean(win)) - ref_mean) / ref_std + abs(float(np.std(win)) - ref_std) / ref_std)
        method_scores["entropy_delta"].append(abs(_entropy(hist) - ref_entropy))
    elapsed = perf_counter() - start_time

    results = {}
    starts_arr = np.asarray(starts)
    pre_mask = starts_arr + window < change
    for method, scores in method_scores.items():
        arr = np.asarray(scores)
        pre = arr[pre_mask]
        threshold = float(np.mean(pre) + 4.0 * np.std(pre)) if pre.size else float(np.percentile(arr, 95))
        fp = float(np.mean(pre > threshold)) if pre.size else 0.0
        post_idx = np.where((starts_arr >= change) & (arr > threshold))[0]
        detected = bool(post_idx.size)
        delay = int(starts_arr[post_idx[0]] - change) if detected else -1
        results[method] = DriftBenchmarkResult(method, scenario, threshold, fp, delay, detected, elapsed / len(method_scores))
    return results


def _entropy(counts: np.ndarray) -> float:
    p = counts / max(float(np.sum(counts)), 1e-12)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))
