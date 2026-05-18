# Performance Scaling

Deep validation run: `results/raw/deep_validation_2026-05-18/performance_scaling/`.

These are safe local scaling checks. They are not production profiling. Memory uses Python `tracemalloc`, not full resident-set-size accounting.

## Stable partition

RDT remains best by the current combined score on uniform data up to 50,000 points. It is not the fastest assignment method; trivial/null controls and simple spatial orderings are faster.

| n | best_score | fastest | rdt_seconds | fastest_seconds | rdt_score | best_score_value |
|---|---|---|---|---|---|---|
| 1000 | rdt_stable | same_counts_shuffled_labels | 0.0066 | 0.0000 | 0.2039 | 0.2039 |
| 5000 | rdt_stable | random_labels | 0.0089 | 0.0001 | 0.2006 | 0.2006 |
| 20000 | rdt_stable | random_labels | 0.0173 | 0.0001 | 0.2005 | 0.2005 |
| 50000 | rdt_stable | random_labels | 0.0370 | 0.0003 | 0.2005 | 0.2005 |

## Cover

Hypothesis-targeted gives the strongest class discovery on the expanded seeded corpus. RDT-cover scales acceptably through budget 2,048 but remains slower than blind random and low-discrepancy samplers.

| budget | best_discovery | fastest | rdt_seconds | fastest_seconds | rdt_classes | best_classes |
|---|---|---|---|---|---|---|
| 128 | hypothesis_targeted | random_uniform | 0.0058 | 0.0001 | 10 | 13 |
| 256 | hypothesis_targeted | random_uniform | 0.0130 | 0.0001 | 10 | 13 |
| 512 | hypothesis_targeted | random_uniform | 0.0321 | 0.0001 | 10 | 13 |
| 1024 | hypothesis_targeted | random_uniform | 0.0672 | 0.0002 | 10 | 13 |
| 2048 | hypothesis_targeted | random_uniform | 0.1413 | 0.0002 | 10 | 13 |

Raw artifacts:

- `results/raw/deep_validation_2026-05-18/performance_scaling/performance_scaling_results.json`
- `results/raw/deep_validation_2026-05-18/performance_scaling/stable_partition_scaling.csv`
- `results/raw/deep_validation_2026-05-18/performance_scaling/cover_scaling.csv`
- `results/raw/deep_validation_2026-05-18/performance_scaling/PERFORMANCE_SCALING_RESULT_CARD.md`
