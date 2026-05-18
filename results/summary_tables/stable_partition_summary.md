# Stable Partition Summary

Deep validation run: `results/raw/deep_validation_2026-05-18/stable_partition/`.

The stable partition result became stronger in this pass. RDT stable labels were the best combined movement/locality/load score in `40` of `40` dataset/resize tasks. The run covered 8 datasets, 5 resize pairs, 3 seeds, geospatial baselines, hash baselines, spatial-order baselines, a remapped-label ablation, shuffled-label null control, and random-label null control.

Allowed interpretation: stable ancestor-label inheritance gives a useful movement/locality/load tradeoff in the tested resize tasks. This remains a tradeoff claim, not a raw speed claim.

| dataset | resize | best | rdt | jump | remap |
|---|---|---|---|---|---|
| anisotropic_gaussian | 16 -> 20 | rdt_stable | 0.1968 | 0.6738 | 0.8943 |
| anisotropic_gaussian | 128 -> 160 | rdt_stable | 0.4722 | 0.7532 | 1.2417 |
| california_housing | 16 -> 20 | rdt_stable | 0.4686 | 0.6746 | 1.2806 |
| california_housing | 128 -> 160 | rdt_stable | 0.4514 | 0.7544 | 1.2598 |
| clustered | 16 -> 20 | rdt_stable | 0.2511 | 0.6746 | 0.9173 |
| clustered | 128 -> 160 | rdt_stable | 0.4899 | 0.7531 | 1.2823 |
| diagonal | 16 -> 20 | rdt_stable | 0.1788 | 0.6750 | 0.8766 |
| diagonal | 128 -> 160 | rdt_stable | 0.1934 | 0.7558 | 1.0475 |
| hotspot_tail | 16 -> 20 | rdt_stable | 0.2340 | 0.6753 | 0.9840 |
| hotspot_tail | 128 -> 160 | rdt_stable | 0.4870 | 0.7509 | 1.2770 |
| ring_annulus | 16 -> 20 | rdt_stable | 0.1878 | 0.6744 | 0.7813 |
| ring_annulus | 128 -> 160 | rdt_stable | 0.1929 | 0.7543 | 1.0319 |
| two_clusters_imbalance | 16 -> 20 | rdt_stable | 0.2049 | 0.6753 | 0.8038 |
| two_clusters_imbalance | 128 -> 160 | rdt_stable | 0.4989 | 0.7476 | 1.2828 |
| uniform | 16 -> 20 | rdt_stable | 0.2005 | 0.6744 | 0.9190 |
| uniform | 128 -> 160 | rdt_stable | 0.1873 | 0.7544 | 1.0099 |

Raw artifacts:

- `results/raw/deep_validation_2026-05-18/stable_partition/stable_partition_results.json`
- `results/raw/deep_validation_2026-05-18/stable_partition/stable_partition_summary.csv`
- `results/raw/deep_validation_2026-05-18/stable_partition/STABLE_PARTITION_RESULT_CARD.md`
