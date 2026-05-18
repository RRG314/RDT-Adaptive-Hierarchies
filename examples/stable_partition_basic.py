"""Basic stable partition example."""

from __future__ import annotations

import numpy as np

from rdt_adaptive_hierarchy import RDTStablePartition
from rdt_adaptive_hierarchy.core.metrics import locality_dispersion, movement_fraction


def main() -> None:
    rng = np.random.default_rng(7)
    points = rng.random((1_000, 2))
    partitioner = RDTStablePartition(max_buckets=32).fit(points)
    labels_16 = partitioner.assign_training(16)
    labels_20 = partitioner.assign_training(20)
    print({
        "movement_16_to_20": round(movement_fraction(labels_16, labels_20), 4),
        "locality_20": round(locality_dispersion(points, labels_20), 4),
        "unique_labels_20": int(len(np.unique(labels_20))),
    })


if __name__ == "__main__":
    main()
