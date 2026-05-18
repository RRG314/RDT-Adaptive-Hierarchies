# RDT-Cover Summary

Submission-validation run: `results/raw/submission_validation_2026-05-18/cover/`.

The seeded numerical corpus has `14` classes. The 10-seed run confirms the narrower interpretation from the prior pass: RDT-cover beats blind random, Sobol, Halton, and Latin hypercube on class discovery, but targeted Hypothesis and the powers-only ablation remain stronger on this corpus.

Allowed interpretation: RDT-cover is a deterministic multiscale edge-case generator that complements random, low-discrepancy, and property-based strategies. It is not generally better than Hypothesis, and it is not yet validated on real bug corpora.

## Seeded Corpus At Budget 2048

| method | classes ±95% CI | hits ±95% CI | hit rate note |
|---|---:|---:|---|
| hypothesis_targeted | 13.00 ± 0.00 | 2562.00 ± 13.88 | strongest because predicates are known |
| powers_only | 11.00 ± 0.00 | 920.50 ± 21.86 | strongest deterministic ablation |
| rdt_cover | 10.00 ± 0.00 | 274.60 ± 5.19 | beats blind space-filling baselines |
| boundary_only | 9.00 ± 0.00 | 561.30 ± 20.70 | simple edge baseline remains strong |
| rdt_hybrid_cover | 9.00 ± 0.00 | 418.10 ± 2.60 | Sobol fill improves coverage, not class count |
| midpoint_only | 6.00 ± 0.00 | 3347.70 ± 0.59 | many hits in fewer classes |
| latin_hypercube | 4.00 ± 0.00 | 539.40 ± 2.85 | blind sampler |
| sobol | 4.00 ± 0.00 | 539.20 ± 1.75 | blind low-discrepancy sampler |
| halton | 4.00 ± 0.00 | 539.00 ± 1.57 | blind low-discrepancy sampler |
| random_uniform | 4.00 ± 0.00 | 532.70 ± 20.57 | blind sampler |

## Property Benchmark

Additional run: `results/raw/submission_validation_2026-05-18/cover_property/`.

This benchmark is separate from the seeded corpus. It evaluates ordinary floating-point properties and includes a targeted Hypothesis `find` baseline. It is still synthetic, but it is closer to property-testing practice because each failure comes from a checked property rather than a named edge-class predicate.

| property | RDT-cover found rate | powers-only found rate | Hypothesis found rate | interpretation |
|---|---:|---:|---:|---|
| division_roundtrip | 1.00 | 1.00 | 1.00 | edge anchors help; blind samplers missed this in the run |
| exp_log_roundtrip | 1.00 | 1.00 | 1.00 | common overflow behavior; many methods find it |
| sqrt_square_overflow | 1.00 | 1.00 | 1.00 | common overflow behavior; many methods find it |
| symmetric_matrix_singularity | 1.00 | 1.00 | 1.00 | structured anchors help; blind samplers missed this in the run |
| tan_periodicity | 0.00 | 0.10 | 0.00 | RDT-cover did not find this failure at budget 512 |

The property run strengthens the claim that deterministic anchors can expose some numerical traps, but it also gives a clear failure case. RDT-cover should not be described as a general fuzzer.

Raw artifacts:

- `results/raw/submission_validation_2026-05-18/cover/cover_results.json`
- `results/raw/submission_validation_2026-05-18/cover/cover_summary.csv`
- `results/raw/submission_validation_2026-05-18/cover/COVER_RESULT_CARD.md`
- `results/raw/submission_validation_2026-05-18/cover_property/cover_property_results.json`
- `results/raw/submission_validation_2026-05-18/cover_property/COVER_PROPERTY_RESULT_CARD.md`
