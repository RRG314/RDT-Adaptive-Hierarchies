# RDT-Cover Summary

## Setup

Task: generate numeric test points in a two-dimensional domain and count predeclared seeded edge-case classes.

Edge classes include zero boundary, large cancellation, power transition, outer corner, and thin annulus.

Baselines: random uniform, Sobol, Latin hypercube.

## Main Result

| Method | Mean bug classes found | Mean total hits |
|---|---:|---:|
| RDT full | 5.00 | 75.20 |
| RDT+Sobol | 5.00 | 70.20 |
| powers-only | 4.00 | 89.40 |
| midpoints-only | 3.00 | 63.00 |
| boundaries-only | 3.00 | 40.00 |
| random uniform | 2.00 | 35.60 |
| Sobol | 2.00 | 34.20 |

## Interpretation

The RDT-specific components matter in the seeded corpus. Powers, midpoints, and boundaries each find part of the failure set. The hybrid keeps full bug-class discovery while improving space fill compared with RDT-only.

## Limitations

The corpus is synthetic and designed around numerical edge classes. Real bug corpora and Hypothesis comparisons are needed before public claims become stronger.

## Raw Artifacts

- `results/raw/ablation_5seed_2026-05-18/ablation_results.json`
- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_results.json`

