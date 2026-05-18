"""Bounded RDT applications.

First-class supported applications are stable partitioning and coverage.
Residual sampling and shell diagnostics are retained as experimental modules.
"""

from .cover import rdt_cover, rdt_hybrid_cover
from .geometry_validation import recursive_depth_geometry, run_geometry_validation
from .residual_sampler import RDTResidualSampler
from .stable_partition import RDTStablePartition

__all__ = [
    "RDTResidualSampler",
    "RDTStablePartition",
    "rdt_cover",
    "rdt_hybrid_cover",
    "recursive_depth_geometry",
    "run_geometry_validation",
]
