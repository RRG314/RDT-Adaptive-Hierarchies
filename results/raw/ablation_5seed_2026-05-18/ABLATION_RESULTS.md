# RDT Ablation Results

Seeds: 0..4

Ablations test which RDT components actually matter. These are validation results, not broad proof.

## Stable Partition Ablation

| Dataset | Resize | Best score | Stable labels score | Remapped labels score | Jump score |
|---|---:|---:|---:|---:|---:|
| real_california_housing | 16->20 | rdt_stable_labels (0.4386) | 0.4386 | 1.2198 | 0.6583 |
| real_california_housing | 64->80 | rdt_stable_labels (0.4641) | 0.4641 | 1.2762 | 0.6790 |
| synthetic_clustered | 16->20 | rdt_stable_labels (0.2639) | 0.2639 | 0.9513 | 0.6601 |
| synthetic_clustered | 64->80 | rdt_stable_labels (0.4426) | 0.4426 | 1.2862 | 0.6933 |
| synthetic_uniform | 16->20 | rdt_stable_labels (0.2003) | 0.2003 | 0.8439 | 0.6599 |
| synthetic_uniform | 64->80 | rdt_stable_labels (0.1828) | 0.1828 | 1.0230 | 0.6934 |

## Residual Sampler Ablation

| Field | Best composite | RDT default | RDT no coverage | RDT no gradient | RDT tuned | Top residual |
|---|---:|---:|---:|---:|---:|---:|
| real_california_housing_residual | top_residual (0.4596) | 0.2879 | 0.2412 | 0.2745 | 0.2846 | 0.4596 |
| synthetic_oscillatory | top_residual (0.8896) | 0.5595 | 0.3241 | 0.5594 | 0.6280 | 0.8896 |
| synthetic_sharp_front | rdt_tuned (0.7241) | 0.6677 | 0.4731 | 0.6688 | 0.7241 | 0.6993 |
| synthetic_two_hotspots | rdt_tuned (0.7762) | 0.7358 | 0.5519 | 0.7420 | 0.7762 | 0.6381 |

## Coverage Ablation

| Method | Bug classes | Total hits | Centered discrepancy |
|---|---:|---:|---:|
| rdt_full | 5.00 | 75.20 | 0.11446 |
| rdt_hybrid_sobol | 5.00 | 70.20 | 0.02822 |
| rdt_powers_only | 4.00 | 89.40 | 0.00108 |
| rdt_midpoints_only | 3.00 | 63.00 | 0.00066 |
| rdt_boundaries_only | 3.00 | 40.00 | 0.00046 |
| random_uniform | 2.00 | 35.60 | 0.00044 |
| sobol | 2.00 | 34.20 | 0.00000 |

## Drift Ablation

| Dataset | Method | Detection rate | False positives before first window |
|---|---|---:|---:|
| real_nab_ambient | entropy_delta | 0.00 | 2.00 |
| real_nab_ambient | histogram_js | 0.00 | 2.00 |
| real_nab_ambient | mean_std | 1.00 | 2.00 |
| real_nab_ambient | rdt_raw_abs_shell | 0.00 | 0.00 |
| real_nab_ambient | rdt_standard_abs_shell | 1.00 | 2.00 |
| real_nab_ambient | rdt_standard_signed_shell | 1.00 | 2.00 |
| synthetic_variance_shift | entropy_delta | 1.00 | 1.00 |
| synthetic_variance_shift | histogram_js | 1.00 | 1.00 |
| synthetic_variance_shift | mean_std | 1.00 | 1.00 |
| synthetic_variance_shift | rdt_raw_abs_shell | 1.00 | 1.00 |
| synthetic_variance_shift | rdt_standard_abs_shell | 1.00 | 1.00 |
| synthetic_variance_shift | rdt_standard_signed_shell | 1.00 | 1.00 |

## Codec Ablation

| Corpus | Best ratio | zlib | RDT delta | Adaptive RDT |
|---|---:|---:|---:|---:|
| real_gutenberg_alice | bz2 (3.5372) | 2.8219 | 2.3085 | 2.8216 |
| synthetic_ramp | rdt_delta_zlib (321.2549) | 40.1569 | 321.2549 | 287.4386 |
| synthetic_random | zlib (0.9993) | 0.9993 | 0.9987 | 0.9990 |

## Validation Readout

- Stable partitioning must show that stable label inheritance matters; if remapped labels match it, the RDT stability claim is weak.
- Residual sampling must show that hierarchy/coverage beats greedy top residuals on real error, not just synthetic selection scores.
- Coverage must show which pieces find which failures; full RDT is only meaningful if shell/power/boundary pieces each explain part of the win.
- Drift must show that standardization is necessary; raw shell depth can be non-informative on real-valued telemetry.
- Codec ablations must show where delta preprocessing helps and where adaptive gating merely avoids damage.
