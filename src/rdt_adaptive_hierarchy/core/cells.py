from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RecursiveCell:
    """Formal recursive cell used by the framework specification."""

    cell_id: int
    parent_id: Optional[int]
    depth: int
    indices: np.ndarray
    split_dim: Optional[int] = None
    threshold: Optional[float] = None
    left_id: Optional[int] = None
    right_id: Optional[int] = None

    @property
    def size(self) -> int:
        return int(self.indices.size)

