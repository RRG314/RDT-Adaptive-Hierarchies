"""Public API for RDT Adaptive Hierarchies.

The top-level namespace exposes the stable release surface. Experimental
research modules remain available from their subpackages, but they are not
promoted as headline package features.
"""

from .core.hierarchy import RDTHierarchy
from .core.metrics import load_imbalance, locality_dispersion, movement_fraction
from .applications.stable_partition import RDTStablePartition
from .applications.cover import rdt_cover, rdt_hybrid_cover

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "RDTHierarchy",
    "RDTStablePartition",
    "rdt_cover",
    "rdt_hybrid_cover",
    "movement_fraction",
    "load_imbalance",
    "locality_dispersion",
]
