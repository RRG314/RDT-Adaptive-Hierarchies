"""RDT Adaptive Hierarchy framework.

This package contains the bounded, evidence-tested framework. It does not claim
that RDT is universal; unsupported applications remain outside the core.
"""

from .core.hierarchy import RDTHierarchy, rdt_depth_int
from .applications.stable_partition import RDTStablePartition
from .applications.cover import rdt_cover, rdt_hybrid_cover
from .applications.residual_sampler import RDTResidualSampler

__all__ = [
    "RDTHierarchy",
    "RDTStablePartition",
    "RDTResidualSampler",
    "rdt_cover",
    "rdt_hybrid_cover",
    "rdt_depth_int",
]

