# Real Public Data Benchmark Results

These results use public datasets and should be read as development evidence, not publication-grade proof.

## Real Stable Partitioning: California Housing Geospatial Points

| k1 -> k2 | Best combined score | RDT score | Morton score | Jump score |
|---|---:|---:|---:|---:|
| 16 -> 20 | rdt_stable (0.4386) | 0.4386 | 0.9195 | 0.6583 |
| 32 -> 40 | rdt_stable (0.4945) | 0.4945 | 0.9674 | 0.6664 |
| 64 -> 80 | rdt_stable (0.4641) | 0.4641 | 0.9830 | 0.6790 |

## Real Residual Sampling: California Housing Local Value Residual

| Method | Composite | Top recall | Mean residual | Coverage entropy |
|---|---:|---:|---:|---:|
| top_residual | 0.4596 | 0.4961 | 0.4841 | 0.4876 |
| top_residual_gradient | 0.4359 | 0.4903 | 0.4713 | 0.4543 |
| residual_proportional | 0.3254 | 0.1298 | 0.2000 | 0.5485 |
| uniform | 0.2927 | 0.0252 | 0.0797 | 0.5540 |
| rdt_residual_tuned | 0.2839 | 0.1483 | 0.2106 | 0.4151 |

## Real Drift: NAB Ambient Temperature

| Method | Detected in labeled window | Delay minutes | False positives before first window |
|---|---:|---:|---:|
| rdt_abs_shell | True | 15060.0 | 0 |
| rdt_signed_shell | False |  | 0 |
| histogram_js | False |  | 0 |
| mean_std | False |  | 0 |
| entropy_delta | False |  | 0 |

## Real Compression Corpora

| Corpus | Best ratio | Adaptive RDT ratio | zlib ratio |
|---|---:|---:|---:|
| california_housing_numeric_csv | lzma (9.4442) | 5.9820 | 5.9823 |
| gutenberg_alice_txt | bz2 (3.5372) | 2.8216 | 2.8219 |
| nab_ambient_temperature_csv | lzma (5.5060) | 3.8670 | 3.8673 |

## Honest Readout

- Real geospatial partitioning is now tested on California Housing coordinates, not only synthetic points.
- Real residual sampling is tested on local house-value residuals; this is a real spatial residual field but still not a PDE/PINN training result.
- Real drift is tested on a labeled NAB time series. Detection alone is not enough; false positives and delay matter.
- Real compression includes public text, real anomaly CSV, and California numeric CSV.
