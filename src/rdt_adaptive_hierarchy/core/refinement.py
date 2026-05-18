from __future__ import annotations

import numpy as np


def select_refinement_cells(scores: np.ndarray, budget: int) -> np.ndarray:
    """Select the top-scoring cells under a refinement budget."""

    scores = np.asarray(scores, dtype=float)
    if budget <= 0:
        return np.array([], dtype=np.int64)
    budget = min(int(budget), scores.size)
    return np.argsort(scores)[-budget:][::-1].astype(np.int64)

