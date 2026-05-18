# Artifact And Null Controls

Submission-validation run: `results/raw/submission_validation_2026-05-18/stable_partition/`.

The stable partition benchmark includes controls that directly test whether the RDT-specific stable-label mechanism matters.

| control | mean combined score across 60 tasks |
|---|---:|
| rdt_stable | 0.3263 |
| rdt_remapped_centroid | 1.0402 |
| same_counts_shuffled_labels | 1.5224 |
| random_labels | 1.4747 |

Interpretation: remapped centroid labels, same-count shuffled labels, and random labels are all worse on the combined score. This supports the mechanism claim that stable ancestor-label inheritance matters in these resize tasks.

Automated stress tests now cover:

- duplicate points mixed with ordinary points,
- all-points-same degeneracy,
- high-dimensional feature arrays,
- adversarial input ordering on smooth uniform data.

Those tests assert valid labels, finite movement/locality/load metrics, and stable behavior under the stress condition. They are correctness and artifact-control tests, not evidence of production-scale performance.

Remaining controls before submission:

- production-style shard migration workloads,
- larger real geospatial and vector workloads,
- parameter sensitivity for virtual-node counts, H3/S2/geohash levels, and score weights,
- isolated per-method memory profiling.
