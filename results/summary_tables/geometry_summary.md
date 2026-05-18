# Geometry Validation Summary

Deep validation run: `results/raw/deep_validation_2026-05-18/geometry/`.

The known-form disk/sphere/cone/cube/cylinder check remains bounded and passes. The new simple-integral checks make the claim narrower: RDT is not generally better than Sobol/QMC on standard integration tasks. It remains a bounded numerical validation object, not a new geometry theory.

| target | best | rdt_rel_err | sobol_rel_err | mc_rel_err |
|---|---|---|---|---|
| annulus_area_unit_square | sobol_qmc | 0.007401 | 0.002102 | 0.032128 |
| smooth_sin_cos | sobol_qmc | 0.000126 | 0.000000 | 0.005912 |
| triangle_indicator | sobol_qmc | 0.013184 | 0.000000 | 0.015137 |
| unit_interval_x2 | sobol_qmc | 0.000002 | 0.000000 | 0.011828 |
| unit_square_xy | coarse_midpoint_grid | 0.000000 | 0.000000 | 0.019082 |

Raw artifacts:

- `results/raw/deep_validation_2026-05-18/geometry/geometry_results.json`
- `results/raw/deep_validation_2026-05-18/geometry/geometry_summary.csv`
- `results/raw/deep_validation_2026-05-18/geometry/geometry_integral_summary.csv`
- `results/raw/deep_validation_2026-05-18/geometry/GEOMETRY_RESULT_CARD.md`
