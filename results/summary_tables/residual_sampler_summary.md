# Residual Sampler Summary

## Setup

Task: select candidate points from residual fields using residual score, gradient proxy, and coverage pressure.

Baselines: top residual, top residual plus gradient, residual proportional, uniform.

## Main Result

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| synthetic sharp front | RDT tuned | 0.7241 | 0.6993 |
| synthetic two hotspots | RDT tuned | 0.7762 | 0.6381 |
| synthetic oscillatory | top residual | 0.6280 | 0.8896 |
| real California residual | top residual | 0.2839 | 0.4596 |

## Interpretation

The residual sampler is mixed. It can help when coverage matters and the field has separated hotspots, but it loses when the metric rewards aggressive selection of the largest residuals.

## Limitation

These are point-selection metrics. They are not PDE or PINN training results.

## Raw Artifacts

- `results/raw/ablation_5seed_2026-05-18/ablation_results.json`
- `results/raw/real_public_data_2026-05-18/real_public_data_results.json`

