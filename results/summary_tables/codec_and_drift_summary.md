# Codec And Drift Summary

These results are kept as boundary evidence. They explain what should not be promoted.

![Runtime caveat](../../docs/figures/performance_50k_uniform.svg)

## Shell Drift

Shell drift can detect some synthetic shifts, but simple baselines such as mean/std and histogram divergence are competitive or better. On the real NAB ambient-temperature pass, the evidence did not support a strong detector claim.

Conclusion: shell drift is diagnostic-only.

## Recursive Delta Codec

The recursive delta transform helps ramp-like synthetic data:

| Corpus | Best method | RDT delta | zlib |
|---|---|---:|---:|
| synthetic ramp | RDT delta | 321.2549 | 40.1569 |
| real Gutenberg Alice | bz2 | 2.3085 | 2.8219 |
| synthetic random | zlib | 0.9987 | 0.9993 |

Conclusion: recursive delta preprocessing is narrow and is not a general compressor.

The useful lesson is negative: RDT-style transforms should not be promoted as compression unless they pass exact roundtrip tests, include header/model cost, and beat zlib/bz2/lzma on real corpora. Current evidence does not meet that bar.

## Raw Artifacts

- `results/raw/ablation_5seed_2026-05-18/ablation_results.json`
- `results/raw/real_public_data_2026-05-18/real_public_data_results.json`
