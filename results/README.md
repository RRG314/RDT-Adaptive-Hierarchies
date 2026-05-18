# Results

This directory contains the current evidence snapshot for RDT Adaptive Hierarchies. The purpose is not to preserve every exploratory number. It is to make the public claims traceable: what worked, what failed, what was synthetic-only, what used public data, and what still needs stronger baselines.

The most recent expanded validation run was produced on 2026-05-18. It uses repeated seeds for synthetic benchmarks, public California Housing data where noted, and the benchmark scripts in `src/rdt_adaptive_hierarchy/benchmarks/`.

## Result Summary

| Area | Best current readout | Status |
|---|---|---|
| Stable partitioning | RDT stable labels had the best tested combined movement/locality/load score in `40/40` dataset/resize tasks. | Strongest current result. This is a tradeoff claim, not a raw speed claim. |
| RDT-cover | On the expanded 14-class seeded corpus at budget `1024`, Hypothesis found `13/14` classes, powers-only found `11/14`, RDT-cover found `10/14`, and blind random/Sobol/Halton/Latin found `4/14`. | Useful deterministic edge coverage, but narrower than earlier results. Not better than targeted Hypothesis or tuned power anchors. |
| Geometry validation | Known-form checks pass with low error, but Sobol/QMC beats RDT on several simple integral checks. | Bounded numerical validation object. Not a new geometry theory. |
| Residual sampling | RDT variants help selected synthetic hotspot fields, but lose on California residuals and other fields. | Mixed. Research-only. |
| Shell drift | Some synthetic detection, but simple baselines remain competitive. | Diagnostic-only. |
| Recursive delta codec | Wins on ramp-like synthetic bytes, loses on real text and CSV corpora. | Narrow transform observation only. |

## Stable Partitioning

The stable partition benchmark asks whether a partition can resize while controlling three costs:

- movement: fraction of points whose label changes,
- locality: within-label spread relative to global spread,
- load imbalance: largest bucket size divided by the average nonempty bucket size.

The combined score is:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

Lower is better. The expanded run covers uniform, clustered, diagonal, hotspot-tail, anisotropic Gaussian, ring/annulus, two-cluster imbalance, and California Housing coordinate datasets across resize pairs `8 -> 10`, `16 -> 20`, `32 -> 40`, `64 -> 80`, and `128 -> 160`.

### California Housing Coordinates

The real-data check uses longitude/latitude-like coordinates from the scikit-learn California Housing dataset with `n = 20,640`.

| Resize | RDT stable | Jump Hash | Rendezvous Hash | Grid | Morton sort | Principal sort |
|---|---:|---:|---:|---:|---:|---:|
| 16 -> 20 | 0.4686 | 0.6746 | 0.6759 | 1.9268 | 0.9208 | 0.8939 |
| 32 -> 40 | 0.4695 | 0.7174 | 0.6812 | 2.0430 | 0.9682 | 0.9531 |
| 64 -> 80 | 0.4706 | 0.7219 | 0.7763 | 3.6256 | 0.9889 | 0.9846 |
| 128 -> 160 | 0.4514 | 0.7544 | 0.7546 | 2.9751 | 0.9971 | 0.9991 |

![California Housing resize score](../docs/figures/stable_partition_real.svg)

Interpretation: RDT stable labels are better on this combined score because they move far fewer points than Morton/principal sort while preserving much better locality than hash-only baselines. Grid has very low assignment cost but poor load balance under these tested bucket counts.

### Mechanism And Null Controls

The most important test is the stable-label ablation. RDT with remapped centroid labels uses the same recursive structure but discards the stable inheritance rule. It performs much worse:

![Stable label ablation](../docs/figures/stable_partition_ablation.svg)

Representative scores:

| Dataset | Resize | Stable labels | Remapped labels | Jump Hash |
|---|---:|---:|---:|---:|
| California Housing | 16 -> 20 | 0.4686 | 1.2806 | 0.6746 |
| California Housing | 64 -> 80 | 0.4706 | 1.2612 | 0.7219 |
| Synthetic uniform | 16 -> 20 | 0.2005 | 0.9190 | 0.6744 |
| Synthetic clustered | 16 -> 20 | 0.2511 | 0.9173 | 0.6746 |

Across the expanded run, mean combined scores were:

| Method | Mean combined score |
|---|---:|
| RDT stable | 0.2905 |
| RDT remapped centroid | 0.8620 |
| Same-count shuffled labels | 1.0806 |
| Random labels | 1.0625 |

This supports the mechanism claim: stable ancestor-label inheritance is doing useful work. The result does not prove general superiority over all spatial partitioning systems.

### Companion Spatial Index Repository

The companion [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index) repository contains the range-query and kNN-oriented indexing line. This repository does not fold that code into the adaptive-hierarchy package. It cites the spatial-index repo as related evidence and keeps the active claim here focused on stable resize partitioning.

## RDT-Cover

RDT-cover generates deterministic test inputs around boundaries, midpoints, powers of ten, powers of two, corners, and shell-like scale changes. The expanded benchmark counts 14 seeded numerical edge-case classes.

At budget `1024`:

| Method | Mean classes found | Mean total hits | Mean centered discrepancy |
|---|---:|---:|---:|
| Hypothesis-targeted | 13.00 | 1294.33 | 0.02402 |
| Powers-only | 11.00 | 661.33 | 0.00472 |
| RDT full | 10.00 | 199.67 | 0.11849 |
| Boundary-only | 9.00 | 306.67 | 0.00024 |
| RDT+Sobol | 9.00 | 256.33 | 0.02905 |
| Random uniform | 4.00 | 278.33 | 0.00024 |
| Sobol | 4.00 | 268.67 | 0.00000 |
| Halton | 4.00 | 270.67 | 0.00000 |
| Latin hypercube | 4.00 | 272.33 | 0.00002 |

![RDT-cover edge-case discovery](../docs/figures/coverage_ablation.svg)

Interpretation: deterministic edge anchors explain the RDT-cover win over blind random and low-discrepancy baselines. The stronger result is also a limitation: Hypothesis-targeted coverage and the powers-only ablation beat full RDT-cover on this synthetic corpus. RDT-cover remains useful as a deterministic property-free schedule; it is not superior to targeted property-based testing in this benchmark.

## Geometry Validation

The geometry validation module checks known formulas for disk area, sphere volume, cone volume, cube volume, and cylinder volume, then adds simple integral checks.

Known-form result:

| Method | Max relative error | Mean relative error |
|---|---:|---:|
| RDT recursive-depth | 0.0003674 | 0.0000738 |
| Coarse midpoint baseline | 0.0004025 | 0.0001083 |

Simple integral result:

| Target | Best method | RDT relative error | Sobol relative error |
|---|---|---:|---:|
| Annulus area | Sobol/QMC | 0.007401 | 0.002102 |
| Smooth sine/cosine | Sobol/QMC | 0.000126 | 0.000000 |
| Triangle indicator | Sobol/QMC | 0.013184 | 0.000000 |
| Unit interval `x^2` | Sobol/QMC | 0.000002 | 0.000000 |
| Unit square `xy` | Coarse midpoint grid | 0.000000 | 0.000000 |

![Geometry validation error](../docs/figures/geometry_error.svg)

Interpretation: this is a bounded known-form validation. It does not establish a new geometry theory or a generally better integration method.

## Residual Sampling

The residual sampler selects candidate points using residual magnitude, a gradient proxy, shell/depth metadata, and coverage pressure. Its evidence is mixed:

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| California residual | Top residual | 0.4463 | 0.6869 |
| Multi-front | Top residual gradient | 0.6855 | 0.7583 |
| Oscillatory | Grid-stratified residual | 0.6196 | 0.8910 |
| Sharp front | RDT no gradient | 0.7426 | 0.7314 |
| Two hotspots | RDT tuned | 0.8563 | 0.6588 |

![Residual sampler real-data failure](../docs/figures/residual_real.svg)

Interpretation: RDT coverage helps on selected separated-hotspot fields, but greedy or stratified residual selection is better in other cases. No PDE/PINN training claim is supported.

## Runtime Caveat

RDT stable partitioning is not promoted as the fastest raw assignment method.

![Runtime caveat](../docs/figures/performance_50k_uniform.svg)

In a safe local scaling run on uniform points, RDT stable labels remained best by combined score through `50,000` points, but simple methods and null controls were faster. Public claims should focus on the movement/locality/load tradeoff.

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

- `raw/deep_validation_2026-05-18/stable_partition/stable_partition_results.json`
- `raw/deep_validation_2026-05-18/cover/cover_results.json`
- `raw/deep_validation_2026-05-18/residual_sampler/residual_sampler_results.json`
- `raw/deep_validation_2026-05-18/geometry/geometry_results.json`
- `raw/deep_validation_2026-05-18/performance_scaling/performance_scaling_results.json`
- `raw/release_hardening_2026-05-18/stable_partition/stable_partition_results.json`
- `raw/release_hardening_2026-05-18/cover/cover_results.json`

Rerun commands are documented in `docs/reproducibility.md`.
