# Residual Sampler Summary

Deep validation run: `results/raw/deep_validation_2026-05-18/residual_sampler/`.

Residual sampling remains research-only. RDT variants help on selected synthetic fields, but they lose on the real California residual field and do not dominate greedy residual baselines. This result weakens any broad residual-sampling claim and preserves only a narrow diagnostic/research use.

| field | best | best_score | rdt_tuned | top_residual |
|---|---|---|---|---|
| california_residual | top_residual | 0.6869 | 0.4463 | 0.6869 |
| multi_front | top_residual_gradient | 0.7604 | 0.6855 | 0.7583 |
| oscillatory | grid_stratified_residual | 0.8933 | 0.6196 | 0.8910 |
| sharp_front | rdt_no_gradient | 0.7491 | 0.7426 | 0.7314 |
| two_hotspots | rdt_residual_tuned | 0.8563 | 0.8563 | 0.6588 |

Raw artifacts:

- `results/raw/deep_validation_2026-05-18/residual_sampler/residual_sampler_results.json`
- `results/raw/deep_validation_2026-05-18/residual_sampler/residual_sampler_summary.csv`
- `results/raw/deep_validation_2026-05-18/residual_sampler/RESIDUAL_SAMPLER_RESULT_CARD.md`
