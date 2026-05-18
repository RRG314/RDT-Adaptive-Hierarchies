# RDT Competitive Aggregate Results

Seeds: 0..4
Deep mode: True

These aggregate results are still bounded synthetic/controlled benchmarks. They are suitable for development decisions, not broad publication claims.

## Stable Partitioning

| Dataset | Best mean combined score | RDT movement mean | Jump movement mean | RDT locality mean | Jump locality mean |
|---|---:|---:|---:|---:|---:|
| clustered | rdt_stable (0.2967) | 0.1561 | 0.2012 | 0.0162 | 0.9977 |
| diagonal | rdt_stable (0.1769) | 0.1251 | 0.2012 | 0.0037 | 0.9980 |
| hotspot_tail | rdt_stable (0.4431) | 0.1293 | 0.2012 | 0.0307 | 0.9977 |
| uniform | rdt_stable (0.1907) | 0.1252 | 0.2012 | 0.0342 | 0.9978 |

## Residual Sampling

| Field | Best mean composite | RDT mean | Tuned RDT mean | Top residual mean | Uniform mean |
|---|---:|---:|---:|---:|---:|
| oscillatory | top_residual (0.8905) | 0.5659 | 0.6336 | 0.8905 | 0.5708 |
| sharp_front | rdt_residual_tuned (0.7285) | 0.6463 | 0.7285 | 0.7170 | 0.5687 |
| two_hotspots | rdt_residual_tuned (0.7531) | 0.7161 | 0.7531 | 0.6353 | 0.5704 |

## RDT Coverage

| Method | Mean bug classes found | Mean total hits | Mean min pairwise distance | Mean centered discrepancy |
|---|---:|---:|---:|---:|
| rdt_cover | 5.00 | 83.00 | 0.9353 | 0.11698 |
| rdt_hybrid_cover | 5.00 | 78.40 | 1 | 0.02870 |
| random_uniform | 2.00 | 48.60 | 1083 | 0.00024 |
| latin_hypercube | 2.00 | 46.60 | 2872 | 0.00002 |
| sobol | 2.00 | 45.60 | 1.113e+04 | 0.00000 |

## Shell Drift

| Scenario | Best detection | RDT abs-shell detection/delay | RDT signed-shell detection/delay | Histogram detection/delay | Mean/std detection/delay |
|---|---:|---:|---:|---:|---:|
| mean_shift | histogram_js | 1.00/25.6 | 1.00/0.0 | 1.00/0.0 | 1.00/0.0 |
| scale_mixture | mean_std | 1.00/6.4 | 1.00/6.4 | 1.00/25.6 | 1.00/0.0 |
| tail_shift | entropy_delta | 1.00/0.0 | 1.00/0.0 | 1.00/0.0 | 1.00/0.0 |
| variance_shift | entropy_delta | 1.00/0.0 | 1.00/0.0 | 1.00/0.0 | 1.00/0.0 |

## Transform Codec

| Corpus | Best mean ratio | RDT delta mean ratio | zlib mean ratio | Roundtrip ok rate |
|---|---:|---:|---:|---:|
| blocks | lzma (50.5679) | 39.8637 | 28.9726 | 1.00 |
| ramp | rdt_delta_zlib (520.1270) | 520.1270 | 67.9834 | 1.00 |
| random | zlib (0.9995) | 0.9992 | 0.9995 | 1.00 |
| repeated_text | bz2 (208.7134) | 173.3757 | 202.2716 | 1.00 |

## Development Decisions

- Develop `rdt-stable-partition` if it continues to win the combined movement/locality/load score against the stronger Morton/principal-sort baselines.
- Develop `rdt-cover` as an edge-case complement to Sobol/Hypothesis, especially if hybrid coverage keeps bug discovery while improving discrepancy.
- Continue `rdt-residual-sampler` only if the tuned/hierarchical version beats greedy and stratified baselines on full PDE/PINN error, not just selection metrics.
- Keep `rdt-shell-drift` diagnostic only unless signed-shell drift beats histogram/mean baselines on real telemetry-like data.
- Keep recursive delta preprocessing narrow; the adaptive wrapper can prevent obvious regressions but does not create a general compressor.
