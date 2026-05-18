# Stable Partition Summary

![California Housing resize score](../../docs/figures/stable_partition_real.svg)

## Setup

Task: resize partition labels while balancing movement, locality, and load.

Metric: lower combined score is better:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

Baselines: Jump Hash, virtual-node consistent hashing, rendezvous hashing, Morton sort, Hilbert sort, H3, S2, geohash, grid, principal sort, and modulo hash.

## Main Result

On real California Housing coordinates:

| Resize | RDT stable | Jump Hash | Morton |
|---|---:|---:|---:|
| 16->20 | 0.4386 | 0.6583 | 0.9195 |
| 32->40 | 0.4945 | 0.6664 | 0.9674 |
| 64->80 | 0.4641 | 0.6790 | 0.9830 |

The stable-label ablation is stronger evidence than the headline score. Remapped labels lose on every tested resize task, which supports the claim that ancestor-label inheritance is doing real work.

![Stable label ablation](../../docs/figures/stable_partition_ablation.svg)

## What The Numbers Mean

Jump Hash has low movement but weak locality because it hashes labels without using geometry. Morton sort preserves spatial order but moves many points under the tested resize. RDT stable labels keep enough ancestry to reduce movement while preserving more locality than the hash baselines.

## Limitations

RDT is not the fastest raw method. In 50k synthetic timing checks, grid and Morton were faster. The current claim is a tradeoff claim, not a speed claim.

## Release-Hardening Baselines

The 2026-05-18 release-hardening run adds Hilbert ordering, H3 ordering, S2 ordering, geohash ordering, and virtual-node consistent hashing. RDT stable labels remained the best combined score on the tested synthetic datasets:

| Dataset | RDT stable | Jump Hash | Virtual-node hash | Best added spatial baseline |
|---|---:|---:|---:|---:|
| uniform | 0.2005 ± 0.0003 | 0.6757 ± 0.0001 | 0.7346 ± 0.0004 | Hilbert 0.9050 ± 0.0003 |
| clustered | 0.2739 ± 0.0202 | 0.6760 ± 0.0002 | 0.7347 ± 0.0002 | Morton 0.9012 ± 0.0014 |
| diagonal | 0.1784 ± 0.0002 | 0.6758 ± 0.0001 | 0.7346 ± 0.0004 | Principal sort 0.8771 ± 0.0000 |

Peak Python memory in this run was about `26,957 KiB`.

Remaining missing work includes larger real workloads, memory RSS profiling, and production-style virtual-node tuning.

## Raw Artifacts

- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_results.json`
- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_summary.csv`
- `results/raw/real_public_data_2026-05-18/real_public_data_results.json`
- `results/raw/artifact_performance_5seed_2026-05-18/artifact_check_results.json`
- `results/raw/release_hardening_2026-05-18/stable_partition/stable_partition_results.json`
