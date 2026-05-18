# Statistical Rigor

The submission-validation run uses repeated seeds where randomness is meaningful.

- Stable partition: 10 seeds across 12 workloads and 5 resize pairs. Tables report mean and 95% confidence intervals for movement, locality, imbalance, and combined score.
- Targeted full geospatial stable partition: 10 seeds across California Housing and public US cities with rendezvous hashing, H3, S2, geohash, virtual-node hashing, spatial-order baselines, and null controls.
- RDT-cover seeded corpus: 10 seeds across budgets 128, 256, 512, 1024, and 2048. Tables report mean and 95% confidence intervals for classes found, total hits, hit rate, first hit index, and discrepancy.
- RDT-cover property benchmark: 10 seeds at budget 512 across five floating-point properties. The result reports found rate, first failure index, runtime, and RSS snapshots.
- Residual sampler: still from the prior 3-seed deep-validation pass and remains research-only.
- Geometry: deterministic known-form and integral checks. Confidence intervals are not meaningful for deterministic midpoint/Sobol grids at fixed budget; stochastic Monte Carlo variance should be expanded in a later pass.

Current limitation: the main supported stable-partition claim now has more seeds, but it still needs larger production-style workloads and task-specific scoring choices before paper submission.
