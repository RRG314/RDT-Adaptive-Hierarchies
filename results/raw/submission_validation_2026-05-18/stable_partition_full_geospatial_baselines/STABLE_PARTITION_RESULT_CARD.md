# Stable Partition Result Card

Lower combined score is better. The score is movement + 0.45 * locality + 0.20 * load penalty.

| Dataset | Resize | Best method | RDT score ±95% CI | Jump score ±95% CI | Morton score ±95% CI | Peak RSS KiB |
|---|---:|---|---:|---:|---:|---:|
| california_housing | 8 -> 10 | `rdt_stable` | 0.4473 ± 0.0009 | 0.6558 ± 0.0005 | 0.8301 ± 0.0030 | 124512 |
| california_housing | 16 -> 20 | `rdt_stable` | 0.4673 ± 0.0162 | 0.6748 ± 0.0005 | 0.9210 ± 0.0029 | 124848 |
| california_housing | 32 -> 40 | `rdt_stable` | 0.4698 ± 0.0099 | 0.7177 ± 0.0007 | 0.9670 ± 0.0031 | 124992 |
| california_housing | 64 -> 80 | `rdt_stable` | 0.4728 ± 0.0109 | 0.7218 ± 0.0010 | 0.9887 ± 0.0021 | 125584 |
| california_housing | 128 -> 160 | `rdt_stable` | 0.4464 ± 0.0061 | 0.7540 ± 0.0013 | 0.9973 ± 0.0010 | 122960 |
| us_cities | 8 -> 10 | `rdt_stable` | 0.2311 ± 0.0030 | 0.6561 ± 0.0004 | 0.8482 ± 0.0008 | 123616 |
| us_cities | 16 -> 20 | `rdt_stable` | 0.1995 ± 0.0004 | 0.6750 ± 0.0005 | 0.9378 ± 0.0012 | 123616 |
| us_cities | 32 -> 40 | `rdt_stable` | 0.4516 ± 0.0003 | 0.7180 ± 0.0004 | 0.9747 ± 0.0011 | 123616 |
| us_cities | 64 -> 80 | `rdt_stable` | 0.4521 ± 0.0036 | 0.7214 ± 0.0008 | 0.9935 ± 0.0004 | 123024 |
| us_cities | 128 -> 160 | `rdt_stable` | 0.4641 ± 0.0023 | 0.7543 ± 0.0008 | 0.9991 ± 0.0006 | 120848 |
