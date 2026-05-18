# Figures Plan

This file lists the figures that already exist and how they would be used in a future methods paper.

## Figure 1: Stable Ancestor-Label Inheritance

File: `docs/figures/rdt_stable_label_mechanism.svg`

Purpose: explain the mechanism before showing results. The figure should appear in the method section near the definition of stable labels.

Caption draft:

When a labeled cell splits, one child inherits the parent label and only the new branch receives a new label. This lets the partition resize by extending the existing hierarchy rather than assigning every active cell from scratch.

## Figure 2: California Housing Resize Score

File: `docs/figures/stable_partition_real.svg`

Purpose: show the strongest real-data stable partition result.

Caption draft:

Combined movement/locality/load score on California Housing coordinates. Lower is better. RDT stable labels outperform Jump Hash and Morton ordering on the tested resize pairs, but this score is a tradeoff metric rather than a raw runtime metric.

## Figure 3: Stable Label Ablation

File: `docs/figures/stable_partition_ablation.svg`

Purpose: show that stable ancestor-label inheritance is the working mechanism.

Caption draft:

Holding the recursive structure fixed, remapping labels loses to stable ancestor-label inheritance on representative real and synthetic resize tasks. This supports the claim that stable label inheritance matters, not just recursive splitting.

## Figure 4: RDT-Cover Edge-Case Discovery

File: `docs/figures/coverage_ablation.svg`

Purpose: show RDT-cover as the second supported application.

Caption draft:

Mean seeded numerical edge-case classes found at budget `1024` on the expanded 14-class corpus. Hypothesis-targeted coverage found `13/14` classes, powers-only found `11/14`, full RDT-cover found `10/14`, and blind random/Sobol/Halton/Latin hypercube found `4/14`. The benchmark is synthetic and should be followed by real bug-corpus tests. The figure narrows the RDT-cover claim rather than strengthening it.

## Figure 5: Residual Sampler Failure Case

File: `docs/figures/residual_real.svg`

Purpose: keep the paper honest. This figure belongs in the limitations section.

Caption draft:

On a real California Housing residual field, greedy top-residual selection outperforms RDT-tuned residual sampling. The residual sampler remains a research module until it improves downstream solver or training metrics against RAR/RAD-style baselines.

## Figure 6: Geometry Validation Error

File: `docs/figures/geometry_error.svg`

Purpose: show the bounded known-form geometry result.

Caption draft:

Selected known-form geometry validation errors. The RDT schedule slightly improves the coarse midpoint baseline, but stronger quadrature and QMC baselines are required before stronger numerical-method claims.

## Figure 7: Runtime Caveat

File: `docs/figures/performance_50k_uniform.svg`

Purpose: prevent speed overclaims.

Caption draft:

Machine-local timing on 50k synthetic uniform points. RDT is not the fastest raw partitioner; its current contribution is the movement/locality/load tradeoff.

## Missing Figures Before A Paper

- Confidence interval or seed-distribution plots for stable partition scores.
- Runtime and memory scaling across multiple `n`.
- Coverage time-to-first-failure curves.
- Adaptive-random-testing comparison and real bug-corpus evaluation.
- A schematic comparing RDT stable partitioning with Jump Hash and Morton behavior under resize.
