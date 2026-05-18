# Performance Scaling Result Card

These are safe local scaling checks, not production profiling. Memory includes Python `tracemalloc` peak memory and process resident-set-size snapshots.

## Stable partition

| N | Best score method | Fastest method | RDT seconds | Fastest seconds | RDT score | Best score | Peak RSS KiB | RSS delta KiB |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1000 | `rdt_stable` | `same_counts_shuffled_labels` | 0.0088 | 0.0000 | 0.2039 | 0.2039 | 98768 | 4800 |
| 5000 | `rdt_stable` | `random_labels` | 0.0106 | 0.0001 | 0.2006 | 0.2006 | 96880 | 0 |
| 20000 | `rdt_stable` | `random_labels` | 0.0211 | 0.0001 | 0.2005 | 0.2005 | 96032 | 0 |
| 50000 | `rdt_stable` | `random_labels` | 0.0386 | 0.0003 | 0.2005 | 0.2005 | 66912 | 0 |

## RDT-cover

| Budget | Best discovery method | Fastest method | RDT seconds | Fastest seconds | RDT classes | Best classes | Peak RSS KiB | RSS delta KiB |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 128 | `hypothesis_targeted` | `random_uniform` | 0.0088 | 0.0001 | 10 | 13 | 121296 | 54384 |
| 512 | `hypothesis_targeted` | `random_uniform` | 0.0370 | 0.0003 | 10 | 13 | 128320 | 7024 |
| 1024 | `hypothesis_targeted` | `random_uniform` | 0.0795 | 0.0002 | 10 | 13 | 180976 | 52656 |
| 2048 | `hypothesis_targeted` | `random_uniform` | 0.1621 | 0.0002 | 10 | 13 | 211472 | 30496 |
