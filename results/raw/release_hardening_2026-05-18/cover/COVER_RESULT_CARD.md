# RDT-Cover Result Card

Higher bug-class discovery is better. Centered discrepancy is reported as a space-filling diagnostic, not the primary RDT-cover objective.

| Method | Mean bug classes ±95% CI | Mean total hits ±95% CI | Mean discrepancy ±95% CI | Peak Python memory KiB |
|---|---:|---:|---:|---:|
| `hypothesis_targeted` | 5.00 ± 0.00 | 294.60 ± 1.00 | 0.02021 ± 0.00153 | 61799 |
| `rdt_cover` | 5.00 ± 0.00 | 68.40 ± 3.37 | 0.10912 ± 0.00170 | 61799 |
| `rdt_hybrid_cover` | 5.00 ± 0.00 | 63.40 ± 3.75 | 0.02767 ± 0.00126 | 61799 |
| `random_uniform` | 2.00 ± 0.00 | 25.20 ± 1.90 | 0.00082 ± 0.00046 | 61799 |
| `sobol` | 2.00 ± 0.00 | 23.20 ± 0.96 | 0.00000 ± 0.00000 | 61799 |
| `latin_hypercube` | 1.40 ± 0.48 | 21.80 ± 1.44 | 0.00008 ± 0.00003 | 61799 |
