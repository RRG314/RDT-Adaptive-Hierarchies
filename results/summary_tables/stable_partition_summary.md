# Stable Partition Summary

Submission-validation run: `results/raw/submission_validation_2026-05-18/stable_partition/`.

The stable partition result strengthened in this pass. RDT stable labels had the best combined movement/locality/load score in `60/60` dataset/resize tasks. The run covered 12 workloads, 5 resize pairs, 10 seeds, hash baselines, virtual-node hashing, spatial-order baselines, Hilbert ordering, optional H3/S2/geohash on geospatial workloads, a remapped-label ablation, shuffled-label null control, and random-label null control.

Allowed interpretation: stable ancestor-label inheritance gives a useful movement/locality/load tradeoff in the tested resize tasks. This remains a tradeoff claim, not a raw speed claim.

## Broad Matrix

| method | mean combined score | tasks |
|---|---:|---:|
| rdt_stable | 0.3263 | 60 |
| jump_hash | 0.7085 | 60 |
| virtual_node_hash | 0.7606 | 60 |
| hilbert_sort | 0.9801 | 60 |
| morton_sort | 0.9896 | 60 |
| principal_sort | 1.0347 | 60 |
| rdt_remapped_centroid | 1.0402 | 60 |
| random_labels | 1.4747 | 60 |
| same_counts_shuffled_labels | 1.5224 | 60 |

## Representative Tasks

| dataset | resize | best | rdt | jump | morton |
|---|---|---|---:|---:|---:|
| california_housing | 16 -> 20 | rdt_stable | 0.4673 | 0.6748 | 0.9210 |
| california_housing | 128 -> 160 | rdt_stable | 0.4464 | 0.7540 | 0.9973 |
| us_cities | 16 -> 20 | rdt_stable | 0.1995 | 0.6750 | 0.9378 |
| us_cities | 128 -> 160 | rdt_stable | 0.4641 | 0.7543 | 0.9991 |
| digits_64d | 16 -> 20 | rdt_stable | 0.5584 | 0.6705 | 1.2926 |
| breast_cancer_features | 16 -> 20 | rdt_stable | 0.3814 | 0.6660 | 1.1519 |
| anisotropic_gaussian | 16 -> 20 | rdt_stable | 0.1971 | 0.6743 | 0.9044 |
| ring_annulus | 16 -> 20 | rdt_stable | 0.1878 | 0.6746 | 0.9100 |

## Targeted Full Geospatial Baseline Slice

Rendezvous hashing is expensive at large bucket counts, so the broad matrix omits it and the targeted geospatial slice includes it. RDT remains best on the California Housing and public US cities coordinate workloads.

| dataset | resize | rdt | jump | rendezvous | virtual-node | h3 | s2 | geohash |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| california_housing | 16 -> 20 | 0.4673 | 0.6748 | 0.6761 | 0.7568 | 0.9068 | 0.9376 | 0.9197 |
| california_housing | 64 -> 80 | 0.4728 | 0.7218 | 0.7757 | 0.7413 | 0.9892 | 0.9916 | 0.9867 |
| california_housing | 128 -> 160 | 0.4464 | 0.7540 | 0.7540 | 0.8048 | 0.9989 | 0.9988 | 0.9959 |
| us_cities | 16 -> 20 | 0.1995 | 0.6750 | 0.6765 | 0.7568 | 0.9837 | 0.9494 | 0.9664 |
| us_cities | 64 -> 80 | 0.4521 | 0.7214 | 0.7754 | 0.7404 | 1.0279 | 0.9965 | 0.9947 |
| us_cities | 128 -> 160 | 0.4641 | 0.7543 | 0.7512 | 0.8038 | 1.0279 | 1.0005 | 1.0000 |

Peak resident-set-size snapshots in the broad run were about `133 MiB`. This is process-level RSS tracking, not isolated per-method memory accounting.

Raw artifacts:

- `results/raw/submission_validation_2026-05-18/stable_partition/stable_partition_results.json`
- `results/raw/submission_validation_2026-05-18/stable_partition/stable_partition_summary.csv`
- `results/raw/submission_validation_2026-05-18/stable_partition/STABLE_PARTITION_RESULT_CARD.md`
- `results/raw/submission_validation_2026-05-18/stable_partition_full_geospatial_baselines/stable_partition_results.json`
