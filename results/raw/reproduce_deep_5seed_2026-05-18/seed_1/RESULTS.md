# RDT Competitive Benchmark Results

These are bounded benchmark results. They do not prove broad RDT superiority.

## Stable Partitioning

| Dataset | Best combined score | RDT movement | Jump movement | RDT locality | Jump locality |
|---|---:|---:|---:|---:|---:|
| clustered | rdt_stable (0.2037) | 0.1562 | 0.2009 | 0.0310 | 0.9991 |
| diagonal | rdt_stable (0.1764) | 0.1250 | 0.2009 | 0.0062 | 0.9994 |
| hotspot_tail | rdt_stable (0.4309) | 0.1562 | 0.2009 | 0.0539 | 0.9986 |
| uniform | rdt_stable (0.1820) | 0.1250 | 0.2009 | 0.0563 | 0.9989 |

## Residual Sampling

| Field | Best composite | RDT composite | Top residual composite | Uniform composite |
|---|---:|---:|---:|---:|
| oscillatory | top_residual (0.8905) | 0.5669 | 0.8905 | 0.5713 |
| sharp_front | rdt_residual_tuned (0.7294) | 0.6456 | 0.7170 | 0.5694 |
| two_hotspots | rdt_residual_tuned (0.7531) | 0.7159 | 0.6353 | 0.5831 |

## RDT Coverage

| Method | Bug classes found | Total hits | Min pairwise distance | Centered discrepancy |
|---|---:|---:|---:|---:|
| rdt_cover | 5 | 86 | 1 | 0.11823 |
| rdt_hybrid_cover | 5 | 82 | 1 | 0.02942 |
| latin_hypercube | 2 | 46 | 2393 | 0.00002 |
| sobol | 2 | 44 | 1.165e+04 | 0.00000 |
| random_uniform | 2 | 43 | 593.1 | 0.00027 |

## Shell Drift

| Scenario | Best delay | RDT abs-shell detected/delay | RDT signed-shell detected/delay | Histogram detected/delay | Mean/std detected/delay |
|---|---:|---:|---:|---:|---:|
| mean_shift | rdt_shell_js 0 | True/0 | True/0 | True/0 | True/0 |
| scale_mixture | rdt_shell_js 0 | True/0 | True/0 | True/0 | True/0 |
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
