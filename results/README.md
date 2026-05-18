# Results

This directory contains the current evidence snapshot for RDT Adaptive Hierarchies. The goal is not to archive every possible number. The goal is to make the main conclusions traceable: what worked, what failed, what was only synthetic, and what needs stronger baselines.

The stored runs were produced on 2026-05-18. Repeated synthetic benchmarks use seeds `0..4`. Real-data checks use public datasets where available.

## Result Summary

| Area | Best current readout | Status |
|---|---|---|
| Stable partitioning | RDT stable labels win the tested movement/locality/load score on synthetic and California Housing resize tasks. | Strongest current result. Needs Hilbert/H3/S2/geohash and larger workload comparisons. |
| RDT-cover | Full and hybrid RDT-cover find all 5 seeded numerical edge-case classes. Random, Sobol, and Latin hypercube find 2. | Strong controlled result. Needs Hypothesis and real bug corpora. |
| Geometry validation | RDT recursive-depth schedule gives max relative error `0.0003674` on selected known-form checks. Coarse midpoint baseline gives `0.0004025`. | Bounded numerical result. Needs equal-budget quadrature and QMC. |
| Residual sampling | RDT tuned helps two synthetic fields but loses on oscillatory and real California residuals. | Mixed. Research-only. |
| Shell drift | Some synthetic detection, but simple baselines remain competitive. | Diagnostic-only. |
| Recursive delta codec | Wins on ramp-like synthetic bytes, loses on real text and CSV corpora. | Narrow transform observation only. |

## Stable Partitioning

The stable partition benchmark asks whether a partition can resize while controlling three costs:

- movement: fraction of points whose label changes,
- locality: within-label spread relative to global spread,
- load imbalance: largest bucket size divided by the average nonempty bucket size.

The combined score is:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

Lower is better.

### California Housing Coordinates

The real-data check uses longitude/latitude-like coordinates from the scikit-learn California Housing dataset with `n = 20,640`.

| Resize | RDT stable | Jump Hash | Rendezvous Hash | Grid | Morton sort | Principal sort |
|---|---:|---:|---:|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.6585 | 1.9999 | 0.9195 | 0.8942 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.6710 | 2.4919 | 0.9674 | 0.9529 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.6819 | 4.0003 | 0.9830 | 0.9630 |

![California Housing resize score](../docs/figures/stable_partition_real.svg)

Interpretation: RDT stable labels are better on this combined score because they move far fewer points than Morton/principal sort while preserving much better locality than hash-only baselines. Grid has very low assignment cost but poor load balance under these tested bucket counts.

### Mechanism Ablation

The most important test is the stable-label ablation. RDT with remapped centroid labels uses the same recursive structure but discards the stable inheritance rule. It performs much worse:

![Stable label ablation](../docs/figures/stable_partition_ablation.svg)

Representative scores:

| Dataset | Resize | Stable labels | Remapped labels | Jump Hash |
|---|---:|---:|---:|---:|
| California Housing | 16 -> 20 | 0.4386 | 1.2198 | 0.6583 |
| California Housing | 64 -> 80 | 0.4641 | 1.2762 | 0.6790 |
| Synthetic uniform | 16 -> 20 | 0.2003 | 0.8439 | 0.6599 |
| Synthetic clustered | 16 -> 20 | 0.2639 | 0.9513 | 0.6601 |

This supports the mechanism claim: stable ancestor-label inheritance is doing useful work. The result does not prove general superiority over all spatial partitioning systems.

## RDT-Cover

RDT-cover generates deterministic test inputs around boundaries, midpoints, powers of ten, corners, and shell-like scale changes. The benchmark counts predeclared seeded numerical edge-case classes:

- zero boundary,
- large cancellation,
- power transition,
- outer corner,
- thin annulus.

At the tested budget:

| Method | Mean bug classes found | Mean total hits | Mean centered discrepancy |
|---|---:|---:|---:|
| RDT full | 5.00 | 75.20 | 0.11446 |
| RDT+Sobol | 5.00 | 70.20 | 0.02822 |
| Powers-only | 4.00 | 89.40 | 0.00108 |
| Midpoints-only | 3.00 | 63.00 | 0.00066 |
| Boundaries-only | 3.00 | 40.00 | 0.00046 |
| Random uniform | 2.00 | 35.60 | 0.00044 |
| Sobol | 2.00 | 34.20 | 0.00000 |
| Latin hypercube | 2.00 | 46.60 | 0.00002 |

![RDT-cover edge-case discovery](../docs/figures/coverage_ablation.svg)

Interpretation: the deterministic edge anchors explain the win. Powers, midpoints, and boundaries each find part of the seeded failure set. The hybrid keeps full bug-class discovery while improving fill quality relative to RDT-only.

Limitation: this is still a synthetic seeded corpus. It is good mechanism evidence but not a substitute for Hypothesis strategies, fuzzers, adaptive random testing, or real bug corpora.

## Geometry Validation

The geometry validation module checks known formulas for disk area, sphere volume, cone volume, cube volume, and cylinder volume at radii `0.5`, `1.0`, and `2.0`.

| Radius | RDT max relative error | Midpoint baseline max relative error |
|---|---:|---:|
| 0.5 | 0.0003674 | 0.0004025 |
| 1.0 | 0.0003674 | 0.0004025 |
| 2.0 | 0.0003674 | 0.0004025 |

![Geometry validation error](../docs/figures/geometry_error.svg)

Interpretation: this is a bounded known-form validation. It shows the recursive-depth schedule can reproduce selected formulas with low error. It does not establish a new geometry theory, and it still needs equal-budget quadrature, QMC, and more shapes.

## Residual Sampling

The residual sampler selects candidate points using residual magnitude, a gradient proxy, shell/depth metadata, and coverage pressure. Its evidence is mixed:

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| Synthetic sharp front | RDT tuned | 0.7241 | 0.6993 |
| Synthetic two hotspots | RDT tuned | 0.7762 | 0.6381 |
| Synthetic oscillatory | Top residual | 0.6280 | 0.8896 |
| Real California residual | Top residual | 0.2839 | 0.4596 |

![Residual sampler real-data failure](../docs/figures/residual_real.svg)

Interpretation: RDT coverage helps on selected separated-hotspot fields, but greedy residual selection is better when the target metric rewards selecting the largest errors directly. No PDE/PINN training claim is supported.

## Runtime Caveat

RDT stable partitioning is not promoted as the fastest raw assignment method.

![Runtime caveat](../docs/figures/performance_50k_uniform.svg)

Interpretation: the current implementation is fast enough for the tested development runs, but grid and Morton are faster in raw timing checks. Public claims should focus on the movement/locality/load tradeoff.

## Codec And Drift Boundary Results

These results are included to avoid overstating the framework.

Shell drift detects some synthetic shifts, but simple baselines such as histogram divergence and mean/std are competitive or better. It should be used only as a diagnostic view.

Recursive delta preprocessing helps ramp-like synthetic bytes, but standard compressors win on real corpora:

| Corpus | Best method | RDT delta ratio | zlib ratio |
|---|---|---:|---:|
| Synthetic ramp | RDT delta | 321.2549 | 40.1569 |
| Project Gutenberg Alice | bz2 | 2.3085 | 2.8219 |
| Synthetic random | zlib | 0.9987 | 0.9993 |

Interpretation: recursive delta preprocessing is not a general compressor. It is a narrow transform observation.

## Raw Artifacts

The raw files are kept so the summary can be audited:

- `raw/reproduce_deep_5seed_2026-05-18/aggregate_results.json`
- `raw/reproduce_deep_5seed_2026-05-18/aggregate_summary.csv`
- `raw/ablation_5seed_2026-05-18/ablation_results.json`
- `raw/artifact_performance_5seed_2026-05-18/artifact_check_results.json`
- `raw/real_public_data_2026-05-18/real_public_data_results.json`
- `raw/geometry_validation_2026-05-18/geometry_results.json`

Rerun commands are documented in `docs/reproducibility.md`.
