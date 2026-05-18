# Stable Partition Summary

![California Housing resize score](../../docs/figures/stable_partition_real.svg)

## Setup

Task: resize partition labels while balancing movement, locality, and load.

Metric: lower combined score is better:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

Baselines: Jump Hash, Morton sort, grid, principal sort, modulo hash, rendezvous hash.

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

Missing baselines include Hilbert, H3, S2, geohash, and virtual-node consistent hashing.

## Raw Artifacts

- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_results.json`
- `results/raw/reproduce_deep_5seed_2026-05-18/aggregate_summary.csv`
- `results/raw/real_public_data_2026-05-18/real_public_data_results.json`
- `results/raw/artifact_performance_5seed_2026-05-18/artifact_check_results.json`
