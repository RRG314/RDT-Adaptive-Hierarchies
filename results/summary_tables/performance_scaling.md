# Performance Scaling

Submission-validation scaling run: `results/raw/submission_validation_2026-05-18/performance_scaling/`.

These are safe local scaling checks. They are not production profiling. Memory reporting now includes Python `tracemalloc` peak memory and process resident-set-size snapshots through `psutil` when available.

## Stable Partition

RDT remains best by the current combined score on uniform data up to 50,000 points. It is not the fastest assignment method; trivial/null controls and simple spatial orderings are faster.

| n | best_score | fastest | rdt_seconds | fastest_seconds | rdt_score | best_score_value | peak RSS KiB |
|---:|---|---|---:|---:|---:|---:|---:|
| 1000 | rdt_stable | same_counts_shuffled_labels | 0.0088 | 0.0000 | 0.2039 | 0.2039 | 98768 |
| 5000 | rdt_stable | random_labels | 0.0106 | 0.0001 | 0.2006 | 0.2006 | 96880 |
| 20000 | rdt_stable | random_labels | 0.0211 | 0.0001 | 0.2005 | 0.2005 | 96032 |
| 50000 | rdt_stable | random_labels | 0.0386 | 0.0003 | 0.2005 | 0.2005 | 66912 |

## Cover

Hypothesis-targeted gives the strongest class discovery on the expanded seeded corpus. RDT-cover scales acceptably through budget 2,048 but remains slower than blind random and low-discrepancy samplers.

| budget | best_discovery | fastest | rdt_seconds | fastest_seconds | rdt_classes | best_classes | peak RSS KiB |
|---:|---|---|---:|---:|---:|---:|---:|
| 128 | hypothesis_targeted | random_uniform | 0.0088 | 0.0001 | 10 | 13 | 121296 |
| 512 | hypothesis_targeted | random_uniform | 0.0370 | 0.0003 | 10 | 13 | 128320 |
| 1024 | hypothesis_targeted | random_uniform | 0.0795 | 0.0002 | 10 | 13 | 180976 |
| 2048 | hypothesis_targeted | random_uniform | 0.1621 | 0.0002 | 10 | 13 | 211472 |

Raw artifacts:

- `results/raw/submission_validation_2026-05-18/performance_scaling/performance_scaling_results.json`
- `results/raw/submission_validation_2026-05-18/performance_scaling/stable_partition_scaling.csv`
- `results/raw/submission_validation_2026-05-18/performance_scaling/cover_scaling.csv`
- `results/raw/submission_validation_2026-05-18/performance_scaling/PERFORMANCE_SCALING_RESULT_CARD.md`
