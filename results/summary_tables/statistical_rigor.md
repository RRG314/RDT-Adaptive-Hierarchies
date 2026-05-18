# Statistical Rigor

The deep validation run uses repeated seeds where randomness is meaningful.

- Stable partition: 3 seeds across 8 datasets and 5 resize pairs. Tables report mean and 95% confidence intervals for movement, locality, imbalance, and combined score.
- RDT-cover: 3 seeds across budgets 128, 256, 512, and 1024. Tables report mean and 95% confidence intervals for classes found, total hits, and discrepancy.
- Residual sampler: 3 seeds across synthetic fields and the California residual field. Current summary reports means; this remains research-only.
- Geometry: deterministic known-form and integral checks. Confidence intervals are not meaningful for deterministic midpoint/Sobol grids at fixed budget; stochastic Monte Carlo variance should be expanded in a later pass.

Statistical limitation: 3 seeds are enough to catch gross instability, but publication-grade claims should use more seeds, predeclared tests, and larger real workloads.
