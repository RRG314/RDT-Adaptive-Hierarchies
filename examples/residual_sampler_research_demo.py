"""Research-only residual sampler example."""

from __future__ import annotations

import numpy as np

from rdt_adaptive_hierarchy.applications.residual_sampler import (
    RDTResidualSampler,
    evaluate_selection,
    synthetic_residual_field,
)


def main() -> None:
    xs = np.linspace(0, 1, 48)
    xx, yy = np.meshgrid(xs, xs)
    points = np.column_stack([xx.ravel(), yy.ravel()])
    residuals, gradients = synthetic_residual_field(points, "two_hotspots")
    selected = RDTResidualSampler(random_state=0).select(points, residuals, gradients, n_new=128)
    result = evaluate_selection(points, residuals, selected, "rdt_residual", "two_hotspots", runtime=0.0)
    print({
        "status": "research_only",
        "selected": int(result.selected_count),
        "composite_score": float(round(result.composite_score, 4)),
        "top_recall": float(round(result.top_recall, 4)),
    })


if __name__ == "__main__":
    main()
