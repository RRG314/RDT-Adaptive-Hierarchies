# RDT-Cover Summary

![RDT-cover edge-case discovery](../../docs/figures/coverage_ablation.svg)

## Setup

Task: generate numeric test points in a two-dimensional domain and count predeclared seeded edge-case classes.

Edge classes include zero boundary, large cancellation, power transition, outer corner, and thin annulus.

Baselines: random uniform, Sobol, Latin hypercube, and Hypothesis-targeted coverage.

## Main Result

| Method | Mean bug classes found | Mean total hits |
|---|---:|---:|
| Hypothesis-targeted | 5.00 | 294.60 |
| RDT full | 5.00 | 68.40 |
| RDT+Sobol | 5.00 | 63.40 |
| random uniform | 2.00 | 25.20 |
| Sobol | 2.00 | 23.20 |
| Latin hypercube | 1.40 | 21.80 |

## Interpretation

The RDT-specific components matter in the seeded corpus. Powers, midpoints, and boundaries each find part of the failure set. The hybrid keeps full bug-class discovery while improving space fill compared with RDT-only.

The important result is not that RDT-cover has the lowest discrepancy. Sobol has the best discrepancy, as expected, but misses the seeded edge classes. RDT-cover intentionally spends budget on edge anchors, so its value should be judged by failure discovery at fixed budget, not fill quality alone.

The Hypothesis-targeted baseline also finds all five classes and produces more total hits because it searches with predicate-aware strategies. This narrows the RDT-cover claim: RDT-cover is useful when explicit properties are not available or when a deterministic edge schedule is wanted, while Hypothesis is the stronger baseline when the properties are known.

## Limitations

The corpus is synthetic and designed around numerical edge classes. Real bug corpora are needed before public claims become stronger.

## Raw Artifacts

- `results/raw/ablation_5seed_2026-05-18/ablation_results.json`
- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_results.json`
- `results/raw/release_hardening_2026-05-18/cover/cover_results.json`
