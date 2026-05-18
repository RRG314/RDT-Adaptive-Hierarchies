# Stable Partition Result Card

Lower combined score is better. The score is movement + 0.45 * locality + 0.20 * load penalty.

| Dataset | Best method | RDT score ±95% CI | Jump score ±95% CI | Morton score ±95% CI | Peak Python memory KiB |
|---|---|---:|---:|---:|---:|
| clustered | `rdt_stable` | 0.2739 ± 0.0202 | 0.6760 ± 0.0002 | 0.9012 ± 0.0014 | 26946 |
| diagonal | `rdt_stable` | 0.1784 ± 0.0002 | 0.6758 ± 0.0001 | 0.8773 ± 0.0000 | 26957 |
| uniform | `rdt_stable` | 0.2005 ± 0.0003 | 0.6757 ± 0.0001 | 0.9289 ± 0.0043 | 26942 |
