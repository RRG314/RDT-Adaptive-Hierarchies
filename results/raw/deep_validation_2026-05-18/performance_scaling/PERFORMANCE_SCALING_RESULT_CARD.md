# Performance Scaling Result Card

These are safe local scaling checks, not production profiling. Memory is Python `tracemalloc` peak memory.

## Stable partition

| N | Best score method | Fastest method | RDT seconds | Fastest seconds | RDT score | Best score | Peak memory KiB |
|---:|---|---|---:|---:|---:|---:|---:|
| 1000 | `rdt_stable` | `same_counts_shuffled_labels` | 0.0066 | 0.0000 | 0.2039 | 0.2039 | 25706 |
| 5000 | `rdt_stable` | `random_labels` | 0.0089 | 0.0001 | 0.2006 | 0.2006 | 1363 |
| 20000 | `rdt_stable` | `random_labels` | 0.0173 | 0.0001 | 0.2005 | 0.2005 | 4879 |
| 50000 | `rdt_stable` | `random_labels` | 0.0370 | 0.0003 | 0.2005 | 0.2005 | 12027 |

## RDT-cover

| Budget | Best discovery method | Fastest method | RDT seconds | Fastest seconds | RDT classes | Best classes | Peak memory KiB |
|---:|---|---|---:|---:|---:|---:|---:|
| 128 | `hypothesis_targeted` | `random_uniform` | 0.0058 | 0.0001 | 10 | 13 | 14568 |
| 256 | `hypothesis_targeted` | `random_uniform` | 0.0130 | 0.0001 | 10 | 13 | 6363 |
| 512 | `hypothesis_targeted` | `random_uniform` | 0.0321 | 0.0001 | 10 | 13 | 15689 |
| 1024 | `hypothesis_targeted` | `random_uniform` | 0.0672 | 0.0002 | 10 | 13 | 50376 |
| 2048 | `hypothesis_targeted` | `random_uniform` | 0.1413 | 0.0002 | 10 | 13 | 50603 |
