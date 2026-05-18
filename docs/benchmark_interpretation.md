# Benchmark Interpretation

The benchmarks in this repository answer narrow questions. They are not proof of a broad RDT theory. A result is treated as useful only when it has a baseline, a metric, a failure condition, and a reason the RDT-specific mechanism might matter.

## Stable Partitioning

Question:

Can stable ancestor-label inheritance reduce movement while preserving locality and reasonable load during partition resize?

Current answer:

Yes, on the tested synthetic and California Housing resize tasks.

The key real-data table is:

| Resize | RDT stable | Jump Hash | Rendezvous Hash | Morton sort | Principal sort |
|---|---:|---:|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.6585 | 0.9195 | 0.8942 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.6710 | 0.9674 | 0.9529 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.6819 | 0.9830 | 0.9630 |

Why the result matters:

Hashing baselines move relatively few points, but their locality cost is high. Morton and principal sorting preserve more geometry, but in these resize tasks they move many points. RDT stable labels sit in between those design goals and produce the best combined score.

Why this is not a speed claim:

Grid and Morton methods are faster in raw timing checks. The present claim is about a score that includes movement, locality, and load, not throughput dominance.

Release-hardening update:

Hilbert, H3, S2, geohash, and virtual-node consistent hashing are now implemented. On the 5-seed synthetic release-hardening run, RDT stable labels remained best on the tested uniform, clustered, and diagonal datasets. Peak Python benchmark memory was about `26,957 KiB`. This improves baseline coverage, but it does not replace larger real workload tests.

What would weaken the claim:

- Larger real workloads or tuned production baselines match the score.
- RDT fails on larger or more realistic workloads.
- The combined-score weights are changed and the advantage disappears.

## Stable Label Ablation

Question:

Is stable ancestor-label inheritance actually responsible, or is the recursive split structure enough?

Current answer:

The inheritance rule matters. Remapped labels lose badly:

| Dataset | Resize | Stable labels | Remapped labels | Jump Hash |
|---|---:|---:|---:|---:|
| California Housing | 16 -> 20 | 0.4386 | 1.2198 | 0.6583 |
| California Housing | 64 -> 80 | 0.4641 | 1.2762 | 0.6790 |
| Synthetic uniform | 16 -> 20 | 0.2003 | 0.8439 | 0.6599 |
| Synthetic clustered | 16 -> 20 | 0.2639 | 0.9513 | 0.6601 |

Interpretation:

The claim should be phrased as "stable ancestor-label inheritance improves the tested tradeoff," not "recursive partitioning is generally superior."

## RDT-Cover

Question:

Can deterministic RDT coverage find seeded numerical edge-case classes missed by random and low-discrepancy sampling at the same budget?

Current answer:

Yes, in the current seeded benchmark.

| Method | Mean bug classes found | Mean total hits |
|---|---:|---:|
| Hypothesis-targeted | 5.00 | 294.60 |
| RDT full | 5.00 | 68.40 |
| RDT+Sobol | 5.00 | 63.40 |
| Random uniform | 2.00 | 25.20 |
| Sobol | 2.00 | 23.20 |
| Latin hypercube | 1.40 | 21.80 |

Why the result matters:

The component ablation shows that powers, midpoints, and boundaries each explain part of the win. The full schedule is not just a random cloud with a new name.

What changed after Hypothesis integration:

The Hypothesis-targeted baseline also finds all five seeded edge classes. It uses predicate-aware strategies, so it is a much stronger baseline than random, Sobol, or Latin hypercube. RDT-cover should now be described as a deterministic edge schedule that is competitive on the seeded corpus and useful when properties are not yet formalized, not as a replacement for property-based testing.

What this does not support:

It does not show that RDT-cover beats Hypothesis, fuzzing, or adaptive random testing on real bugs. The next step is a real numerical bug or mutant corpus with time-to-first-failure reporting.

## Geometry Validation

Question:

Can the recursive-depth schedule reproduce selected known forms with low error?

Current answer:

Yes, for the included disk, sphere, cone, cube, and cylinder checks.

| Method | Max relative error | Mean relative error |
|---|---:|---:|
| RDT recursive-depth | 0.0003674 | 0.0000738 |
| Coarse midpoint baseline | 0.0004025 | 0.0001083 |

Interpretation:

This is a useful bounded validation result. It does not prove a new geometry theory. It needs equal-budget quadrature, Monte Carlo, and quasi-Monte Carlo baselines.

## Residual Sampler

Question:

Can RDT coverage improve residual point selection?

Current answer:

Mixed.

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| Sharp front | RDT tuned | 0.7241 | 0.6993 |
| Two hotspots | RDT tuned | 0.7762 | 0.6381 |
| Oscillatory | Top residual | 0.6280 | 0.8896 |
| California residual | Top residual | 0.2839 | 0.4596 |

Interpretation:

RDT coverage may help when the residual field has separated regions and coverage pressure is useful. It loses when the objective rewards selecting the largest residuals directly. No PDE/PINN claim should be made from the current evidence.

## Drift And Codec Boundary Evidence

Shell drift:

Shell drift can be inspected as a scale-sensitive diagnostic, but it does not beat simple histogram or mean/std baselines consistently.

Recursive delta preprocessing:

It helps ramp-like synthetic bytes but loses on real text and CSV corpora. It should not be presented as a compressor.

## Bottom Line

Develop:

- `rdt-stable-partition`
- `rdt-cover`

Keep bounded:

- recursive-depth geometry validation

Keep experimental:

- residual sampling
- shell diagnostics

Do not promote:

- general compression,
- cryptography,
- broad physics closure,
- universal entropy or universal RDT claims.
