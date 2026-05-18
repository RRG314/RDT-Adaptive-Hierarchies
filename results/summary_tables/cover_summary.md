# RDT-Cover Summary

Deep validation run: `results/raw/deep_validation_2026-05-18/cover/`.

The expanded numerical corpus has `14` seeded classes. This made the claim narrower. At budget `1024`, Hypothesis-targeted found the most classes, followed by the powers-only ablation. RDT-cover still beats blind random, Sobol, Halton, and Latin hypercube on class discovery, but the ablation shows that power/scale anchors explain a large part of the useful behavior.

Allowed interpretation: RDT-cover is a deterministic multiscale edge-case generator that complements random, low-discrepancy, and property-based strategies. It is not generally better than Hypothesis, and it is not yet validated on real bug corpora.

| method | classes | hits | first_hit | hit_rate |
|---|---|---|---|---|
| hypothesis_targeted | 13.00 ± 0.00 | 1294.33 ± 15.20 | 1.0 | 0.0903 |
| powers_only | 11.00 ± 0.00 | 661.33 ± 5.35 | 1.0 | 0.0461 |
| rdt_cover | 10.00 ± 0.00 | 199.67 ± 4.71 | 1.0 | 0.0139 |
| boundary_only | 9.00 ± 0.00 | 306.67 ± 3.97 | 1.0 | 0.0214 |
| rdt_hybrid_cover | 9.00 ± 0.00 | 256.33 ± 6.43 | 1.0 | 0.0179 |
| midpoint_only | 6.00 ± 0.00 | 1669.67 ± 0.65 | 1.0 | 0.1165 |
| random_uniform | 4.00 ± 0.00 | 278.33 ± 6.23 | 4.0 | 0.0194 |
| latin_hypercube | 4.00 ± 0.00 | 272.33 ± 2.61 | 3.7 | 0.0190 |
| halton | 4.00 ± 0.00 | 270.67 ± 2.61 | 6.0 | 0.0189 |
| sobol | 4.00 ± 0.00 | 268.67 ± 2.85 | 4.0 | 0.0187 |

Raw artifacts:

- `results/raw/deep_validation_2026-05-18/cover/cover_results.json`
- `results/raw/deep_validation_2026-05-18/cover/cover_summary.csv`
- `results/raw/deep_validation_2026-05-18/cover/COVER_RESULT_CARD.md`
