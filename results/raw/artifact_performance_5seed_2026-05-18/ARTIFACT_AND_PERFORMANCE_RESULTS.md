# Artifact And Performance Results

Seeds: 0..4

These checks test whether the RDT results survive scoring changes, null controls, and scaling pressure.

## Score Weight Sensitivity

| Dataset | Resize | RDT winner rate | Jump winner rate | Morton winner rate | Grid winner rate |
|---|---:|---:|---:|---:|---:|
| real_california_housing | 16->20 | 0.64 | 0.36 | 0.00 | 0.00 |
| real_california_housing | 64->80 | 0.64 | 0.36 | 0.00 | 0.00 |
| synthetic_clustered | 16->20 | 0.81 | 0.19 | 0.00 | 0.00 |
| synthetic_clustered | 64->80 | 0.65 | 0.35 | 0.00 | 0.00 |
| synthetic_uniform | 16->20 | 0.96 | 0.04 | 0.00 | 0.00 |
| synthetic_uniform | 64->80 | 1.00 | 0.00 | 0.00 | 0.00 |

## Label Null Controls

| Dataset | Method | Movement vs k1 | Locality | Imbalance |
|---|---|---:|---:|---:|
| real_california_housing | random_uniform_labels | 0.9501 | 0.9989 | 1.0502 |
| real_california_housing | rdt_true_labels | 0.1250 | 0.0302 | 2.5000 |
| real_california_housing | same_counts_shuffled_labels | 0.9401 | 0.9991 | 2.5000 |
| synthetic_clustered | random_uniform_labels | 0.9505 | 0.9980 | 1.0924 |
| synthetic_clustered | rdt_true_labels | 0.2001 | 0.0306 | 1.2500 |
| synthetic_clustered | same_counts_shuffled_labels | 0.9442 | 0.9982 | 1.2500 |
| synthetic_uniform | random_uniform_labels | 0.9490 | 0.9982 | 1.0812 |
| synthetic_uniform | rdt_true_labels | 0.1252 | 0.0557 | 1.2500 |
| synthetic_uniform | same_counts_shuffled_labels | 0.9449 | 0.9980 | 1.2500 |

## Performance Scaling

| Dataset | N | Fastest method | RDT total sec | Jump total sec | Morton total sec | Grid total sec |
|---|---:|---|---:|---:|---:|---:|
| synthetic_clustered | 1000 | grid | 0.003510 | 0.002195 | 0.000251 | 0.000120 |
| synthetic_clustered | 5000 | grid | 0.005958 | 0.011012 | 0.001062 | 0.000466 |
| synthetic_clustered | 20000 | grid | 0.015451 | 0.044166 | 0.004278 | 0.001710 |
| synthetic_clustered | 50000 | grid | 0.034051 | 0.110638 | 0.011489 | 0.004219 |
| synthetic_uniform | 1000 | grid | 0.003505 | 0.002173 | 0.000252 | 0.000118 |
| synthetic_uniform | 5000 | grid | 0.006023 | 0.011009 | 0.001058 | 0.000464 |
| synthetic_uniform | 20000 | grid | 0.015489 | 0.044905 | 0.004430 | 0.001731 |
| synthetic_uniform | 50000 | grid | 0.035011 | 0.110967 | 0.011732 | 0.004229 |

## Interpretation

- If RDT winner rate collapses when locality weight is low, the result is a locality tradeoff rather than a universal partition win.
- If shuffled labels match RDT locality, the locality result is an artifact. If they are much worse, the hierarchy is doing real work.
- If RDT total time grows too quickly, the method may still be useful for offline/stable partition planning but not hot-path assignment.
