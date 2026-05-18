# Benchmark Interpretation

The benchmarks in this repository answer narrow questions. They are not proof of a broad RDT theory. A result is treated as useful only when it has a baseline, a metric, a failure condition, and a reason the RDT-specific mechanism might matter.

## Stable Partitioning

Question:

Can stable ancestor-label inheritance reduce movement while preserving locality and reasonable load during partition resize?

Current answer:

Yes, on the tested synthetic, public geospatial, and sklearn feature resize tasks. The submission-validation run covered 12 workloads, five resize pairs, and 10 seeds. RDT stable labels were the best combined score in `60/60` dataset/resize tasks.

The key real-data table is:

| Resize | RDT stable | Jump Hash | Rendezvous Hash | Morton sort | Principal sort |
|---|---:|---:|---:|---:|---:|
| 16 -> 20 | 0.4673 | 0.6748 | 0.6761 | 0.9210 | 0.8941 |
| 32 -> 40 | 0.4698 | 0.7177 | 0.6807 | 0.9670 | 0.9531 |
| 64 -> 80 | 0.4728 | 0.7218 | 0.7757 | 0.9887 | 0.9847 |
| 128 -> 160 | 0.4464 | 0.7540 | 0.7540 | 0.9973 | 0.9991 |

Why the result matters:

Hashing baselines move relatively few points, but their locality cost is high. Morton and principal sorting preserve more geometry, but in these resize tasks they move many points. RDT stable labels sit in between those design goals and produce the best combined score.

Why this is not a speed claim:

Grid and Morton methods are faster in raw timing checks. The present claim is about a score that includes movement, locality, and load, not throughput dominance.

Deep-validation update:

Hilbert, H3, S2, geohash, virtual-node consistent hashing, and targeted rendezvous hashing are implemented. The submission-validation run added public US cities, sklearn digits PCA, sklearn digits 64D features, sklearn breast-cancer features, RSS snapshots, and automated stress tests for duplicate points, all-same points, high-dimensional inputs, and adversarial ordering. This improves baseline and artifact-control coverage, but it does not replace production-style shard migration workloads or isolated per-method memory profiling.

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
| California Housing | 16 -> 20 | 0.4673 | 1.2684 | 0.6748 |
| California Housing | 64 -> 80 | 0.4728 | 1.2444 | 0.7218 |
| Synthetic uniform | 16 -> 20 | 0.2010 | 0.9164 | 0.6744 |
| Synthetic clustered | 16 -> 20 | 0.2609 | 0.8934 | 0.6746 |

Interpretation:

The claim should be phrased as "stable ancestor-label inheritance improves the tested tradeoff," not "recursive partitioning is generally superior."

## RDT-Cover

Question:

Can deterministic RDT coverage find seeded numerical edge-case classes missed by random and low-discrepancy sampling at the same budget?

Current answer:

Yes, compared with blind random, Sobol, Halton, and Latin hypercube. No, compared with targeted Hypothesis or even the simpler powers-only ablation on the expanded corpus.

At budget `2048` on the 14-class corpus:

| Method | Mean bug classes found | Mean total hits |
|---|---:|---:|
| Hypothesis-targeted | 13.00 | 2562.00 |
| Powers-only | 11.00 | 920.50 |
| RDT full | 10.00 | 274.60 |
| Boundary-only | 9.00 | 561.30 |
| RDT+Sobol | 9.00 | 418.10 |
| Midpoint-only | 6.00 | 3347.70 |
| Random uniform | 4.00 | 532.70 |
| Sobol | 4.00 | 539.20 |
| Halton | 4.00 | 539.00 |
| Latin hypercube | 4.00 | 539.40 |

Why the result matters:

The result still shows that deterministic edge anchors matter: all structured schedules beat blind random and low-discrepancy sampling on class discovery. It also shows that the full RDT schedule is not automatically the best schedule. Power/scale anchors carry much of the class-discovery signal in this synthetic corpus.

What changed after Hypothesis integration:

The Hypothesis-targeted baseline finds the most classes because it uses predicate-aware strategies. RDT-cover should be described as a deterministic edge schedule that can improve blind coverage and produce reproducible test sets when properties are not yet formalized, not as a replacement for property-based testing.

What this does not support:

It does not show that RDT-cover beats Hypothesis, fuzzing, adaptive random testing, or simpler hand-designed edge schedules on real bugs. A new property-style benchmark found that RDT-cover catches several floating-point traps but misses the tangent-periodicity case at budget `512`. The next step is a real numerical bug or mutant corpus with time-to-first-failure reporting.

## Geometry Validation

Question:

Can the recursive-depth schedule reproduce selected known forms with low error?

Current answer:

Yes, for the included disk, sphere, cone, cube, and cylinder checks. The expanded simple-integral checks show a narrower boundary: Sobol/QMC beats RDT on several ordinary integration tasks.

| Method | Max relative error | Mean relative error |
|---|---:|---:|
| RDT recursive-depth | 0.0003674 | 0.0000738 |
| Coarse midpoint baseline | 0.0004025 | 0.0001083 |

Simple integral checks:

| Target | Best method | RDT relative error | Sobol relative error |
|---|---|---:|---:|
| Annulus area | Sobol/QMC | 0.007401 | 0.002102 |
| Smooth sine/cosine | Sobol/QMC | 0.000126 | 0.000000 |
| Triangle indicator | Sobol/QMC | 0.013184 | 0.000000 |
| Unit interval `x^2` | Sobol/QMC | 0.000002 | 0.000000 |
| Unit square `xy` | Coarse midpoint grid | 0.000000 | 0.000000 |

Interpretation:

This is a useful bounded validation result. It does not prove a new geometry theory, and it does not beat QMC on standard integration tasks.

## Residual Sampler

Question:

Can RDT coverage improve residual point selection?

Current answer:

Mixed.

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| Sharp front | RDT no gradient | 0.7426 | 0.7314 |
| Two hotspots | RDT tuned | 0.8563 | 0.6588 |
| Multi-front | Top residual gradient | 0.6855 | 0.7583 |
| Oscillatory | Grid-stratified residual | 0.6196 | 0.8910 |
| California residual | Top residual | 0.4463 | 0.6869 |

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
