# Artifact And Null Controls

Deep validation run: `results/raw/deep_validation_2026-05-18/stable_partition/`.

The stable partition benchmark includes controls that directly test whether the RDT-specific stable-label mechanism matters.

| control | mean_score | runs |
|---|---|---|
| rdt_stable | 0.2976 | 120 |
| rdt_remapped_centroid | 1.0197 | 120 |
| same_counts_shuffled_labels | 1.5354 | 120 |
| random_labels | 1.4690 | 120 |

Interpretation: remapped centroid labels, same-count shuffled labels, and random labels are all worse on the combined score. This supports the mechanism claim that stable ancestor-label inheritance matters in these resize tasks.

Additional stress cases included in this pass:

- anisotropic Gaussian,
- ring/annulus,
- hotspot-tail,
- two imbalanced clusters,
- California Housing coordinates,
- resize up to 128 -> 160.

Remaining controls before publication: explicit duplicate-point stress, all-points-same degeneracy, high-dimensional stress, and adversarial input ordering should be promoted into automated tests.
