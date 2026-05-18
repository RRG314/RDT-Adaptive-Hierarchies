"""Basic RDT-cover example."""

from __future__ import annotations

from rdt_adaptive_hierarchy import rdt_hybrid_cover
from rdt_adaptive_hierarchy.applications.cover import seeded_numeric_bug_predicates


def main() -> None:
    points = rdt_hybrid_cover([(-1e6, 1e6), (-1e6, 1e6)], budget=256, seed=0)
    bugs = seeded_numeric_bug_predicates(points)
    print({
        "points": int(len(points)),
        "bug_classes_found": int(sum(bool(mask.any()) for mask in bugs.values())),
        "classes": [name for name, mask in bugs.items() if bool(mask.any())],
    })


if __name__ == "__main__":
    main()
