# Residual Sampler Result Card

This benchmark is research-only. It tests point selection metrics, not full PDE or PINN training.

| Field | Best method | RDT tuned | Top residual | Uniform |
|---|---|---:|---:|---:|
| california_residual | `top_residual` | 0.4463 | 0.6869 | 0.3275 |
| multi_front | `top_residual_gradient` | 0.6855 | 0.7583 | 0.5655 |
| oscillatory | `grid_stratified_residual` | 0.6196 | 0.8910 | 0.5636 |
| sharp_front | `rdt_no_gradient` | 0.7426 | 0.7314 | 0.5684 |
| two_hotspots | `rdt_residual_tuned` | 0.8563 | 0.6588 | 0.5693 |
