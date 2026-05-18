# Geometry Validation Result Card

This application checks whether the recursive-depth refinement schedule reproduces known closed forms. It does not establish a new geometry theory.

| Method | Runs | Mean max relative error | Mean relative error |
|---|---:|---:|---:|
| `coarse_midpoint_baseline` | 3 | 0.00040250 | 0.00010828 |
| `rdt_recursive_depth` | 3 | 0.00036741 | 0.00007383 |

Status: `experimental_application_supported_by_known_form_checks`.

Failure condition: recursive-depth refinement fails if it does not converge on the known disk/sphere/cone/cube/cylinder formulas or loses to equal-budget standard quadrature under a predeclared budget.
