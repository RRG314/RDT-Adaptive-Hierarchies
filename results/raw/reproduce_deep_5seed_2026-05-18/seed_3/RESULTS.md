# RDT Competitive Benchmark Results

These are bounded benchmark results. They do not prove broad RDT superiority.

## Stable Partitioning

| Dataset | Best combined score | RDT movement | Jump movement | RDT locality | Jump locality |
|---|---:|---:|---:|---:|---:|
| clustered | rdt_stable (0.2030) | 0.1562 | 0.2009 | 0.0311 | 0.9991 |
| diagonal | rdt_stable (0.1764) | 0.1250 | 0.2009 | 0.0062 | 0.9992 |
| hotspot_tail | rdt_stable (0.4312) | 0.1250 | 0.2009 | 0.0520 | 0.9990 |
| uniform | rdt_stable (0.1819) | 0.1250 | 0.2009 | 0.0559 | 0.9990 |

## Residual Sampling

| Field | Best composite | RDT composite | Top residual composite | Uniform composite |
|---|---:|---:|---:|---:|
| oscillatory | top_residual (0.8905) | 0.5638 | 0.8905 | 0.5737 |
| sharp_front | rdt_residual_tuned (0.7353) | 0.6448 | 0.7170 | 0.5658 |
| two_hotspots | rdt_residual_tuned (0.7531) | 0.7158 | 0.6353 | 0.5727 |

## RDT Coverage

| Method | Bug classes found | Total hits | Min pairwise distance | Centered discrepancy |
|---|---:|---:|---:|---:|
| rdt_cover | 5 | 81 | 1 | 0.11471 |
| rdt_hybrid_cover | 5 | 76 | 1 | 0.02813 |
| sobol | 2 | 49 | 1.456e+04 | 0.00000 |
| latin_hypercube | 2 | 49 | 3185 | 0.00002 |
| random_uniform | 2 | 46 | 1505 | 0.00018 |

## Shell Drift

| Scenario | Best delay | RDT abs-shell detected/delay | RDT signed-shell detected/delay | Histogram detected/delay | Mean/std detected/delay |
|---|---:|---:|---:|---:|---:|
| mean_shift | rdt_signed_shell_js 0 | True/96 | True/0 | True/0 | True/0 |
| scale_mixture | rdt_shell_js 0 | True/0 | True/0 | True/64 | True/0 |
| tail_shift | rdt_shell_js 0 | True/0 | True/0 | True/0 | True/0 |
| variance_shift | rdt_shell_js 0 | True/0 | True/0 | True/0 | True/0 |

## Transform Codec

| Corpus | Best ratio | RDT delta ratio | zlib ratio | Roundtrip failures |
|---|---:|---:|---:|---:|
| blocks | lzma (50.5679) | 39.8637 | 28.9726 | 0 |
| ramp | rdt_delta_zlib (520.1270) | 520.1270 | 67.9834 | 0 |
| random | zlib (0.9995) | 0.9992 | 0.9995 | 0 |
| repeated_text | bz2 (208.7134) | 173.3757 | 202.2716 | 0 |


## Honest Overall Conclusion

- RDT stable partitioning is useful when movement and locality are both scored. Jump Hash remains the movement baseline to respect.
- RDT residual sampling is competitive on the synthetic residual-selection objective, but this is not yet full PINN training evidence.
- RDT coverage is strong on seeded numerical edge classes because it explicitly targets shells, boundaries, and scale transitions.
- Shell drift is mixed and should stay diagnostic until it beats histogram/mean baselines more consistently.
- Recursive delta preprocessing is corpus-dependent and should not be claimed as a general compressor.
