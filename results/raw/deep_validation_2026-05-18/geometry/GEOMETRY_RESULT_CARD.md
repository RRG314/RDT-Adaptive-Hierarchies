# Geometry Validation Result Card

This application checks whether the recursive-depth refinement schedule reproduces known closed forms. It does not establish a new geometry theory.

| Method | Runs | Mean max relative error | Mean relative error |
|---|---:|---:|---:|
| `coarse_midpoint_baseline` | 3 | 0.00040250 | 0.00010828 |
| `rdt_recursive_depth` | 3 | 0.00036741 | 0.00007383 |

## Simple integral checks

| Target | Best method | RDT relative error | Sobol relative error | Monte Carlo relative error |
|---|---|---:|---:|---:|
| annulus_area_unit_square | `sobol_qmc` | 0.007401 | 0.002102 | 0.032128 |
| smooth_sin_cos | `sobol_qmc` | 0.000126 | 0.000000 | 0.005912 |
| triangle_indicator | `sobol_qmc` | 0.013184 | 0.000000 | 0.015137 |
| unit_interval_x2 | `sobol_qmc` | 0.000002 | 0.000000 | 0.011828 |
| unit_square_xy | `coarse_midpoint_grid` | 0.000000 | 0.000000 | 0.019082 |

Status: `experimental_application_supported_by_known_form_checks`.

Failure condition: recursive-depth refinement fails if it does not converge on the known disk/sphere/cone/cube/cylinder formulas or loses to equal-budget standard quadrature under a predeclared budget.
