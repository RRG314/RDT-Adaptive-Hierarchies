# RDT Adaptive Hierarchies

RDT Adaptive Hierarchies is a Python research package for deterministic recursive partitions with stable labels, depth metadata, and deterministic coverage schedules. The package is built around a smaller, testable version of the RDT idea: recursive structure is useful when it preserves something measurable during refinement or resize.

The two main applications in this repo are:

1. `rdt-stable-partition`: partition points into buckets, then resize the number of buckets while trading off movement, locality, and load.
2. `rdt-cover`: generate deterministic numerical test cases at boundaries, midpoints, powers of ten, corners, and shell-like scale transitions.

The repo also includes bounded experimental modules for recursive-depth geometry validation, residual sampling, and shell diagnostics. Those modules are documented as limited research tools, not headline claims.

![Stable label inheritance mechanism](docs/figures/rdt_stable_label_mechanism.svg)

## Origin

The Recursive Division Tree line of work began with Steven Reid's Zenodo preprint *Recursive Division Tree: A Log-Log Algorithm for Integer Depth* (DOI `10.5281/zenodo.18012166`). That earlier work studied recursive depth on positive integers. This repository is a later narrowing of the idea into a computational hierarchy over finite numeric point sets.

The important change is scope. The preprint motivates depth and shell structure; this package asks which recursive metadata survives baseline comparison and ablation. The answer here is narrower: stable labels for resize partitioning and deterministic coverage schedules for numerical edge cases.

## Why This Exists

Many systems need to assign points, keys, tasks, or regions to buckets. When the bucket count changes, the assignment should not move everything. Consistent hashing methods are good at minimizing movement, but they normally do not preserve spatial locality. Spatial orderings and grids can preserve locality, but they can move many points during resize or create load imbalance.

RDT stable partitioning tests a different compromise. It builds a deterministic recursive hierarchy, assigns labels to active cells, and preserves ancestor labels when a cell splits. That lets one child keep the parent label while the new branch receives a new label. The package measures whether this mechanism improves the movement/locality/load tradeoff.

Numerical testing has a related finite-budget problem. Random and low-discrepancy sampling fill a space well, but they can miss specific boundary or scale cases. RDT-cover adds deterministic edge anchors before optional Sobol fill, so it is best understood as a complement to standard sampling rather than a replacement.

## What RDT Means Here

In this repository, RDT means a deterministic recursive hierarchy:

- The input is a finite numeric array `X` with shape `(n_points, n_dimensions)`.
- The root cell contains all points.
- Cells are recursively split by a deterministic spread/median rule.
- Each cell has a depth, parent, descendants, and path from the root.
- Active cells receive stable labels.
- During resize, one child inherits the parent label and only the new branch receives a new label.
- Coverage routines can target boundaries, midpoints, powers, corners, and shell-like transitions.

The supported mechanism is stable ancestor-label inheritance plus deterministic coverage. Recursion by itself is not the claim.

## What Is Supported By Current Evidence

The current evidence snapshot is from repeated local benchmark runs on 2026-05-18. It is strong enough for technical review and further development, but not yet enough for a broad theory paper.

| Area | Current evidence | Interpretation |
|---|---|---|
| Stable partitioning | RDT stable labels beat Jump Hash, Morton ordering, grid, modulo hash, rendezvous hash, and remapped-label ablations on the tested combined movement/locality/load score. | Strongest current direction. The claim is a tradeoff claim, not raw speed superiority. |
| RDT-cover | Full RDT-cover and RDT+Sobol found all 5 seeded numerical edge-case classes at fixed budget; random, Sobol, and Latin hypercube found 2. | Promising deterministic edge-case generator. Needs Hypothesis and real bug-corpus comparisons. |
| Geometry validation | Recursive-depth schedule had max relative error `0.0003674` on selected known-form checks; coarse midpoint baseline had `0.0004025`. | Bounded numerical validation result, not a new geometry theory. |
| Residual sampling | RDT tuned wins on selected synthetic sharp-front and two-hotspot fields, but loses to greedy top residual on oscillatory and real California residual fields. | Research-only. No PDE/PINN training claim is supported. |
| Shell drift | Some synthetic shifts are detected, but simple histogram and mean/std baselines are competitive or better. | Diagnostic-only. Not an anomaly detector claim. |
| Recursive delta codec | Helps ramp-like synthetic bytes but loses to standard compressors on text and CSV corpora. | Narrow transform observation. Not a general compressor. |

## Headline Results

### Stable Partitioning

The stable partition benchmark resizes from `k1` buckets to `k2` buckets. Lower combined score is better:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

On California Housing coordinates (`n = 20,640`):

| Resize | RDT stable | Jump Hash | Morton sort | Principal sort |
|---|---:|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.9195 | 0.8942 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.9674 | 0.9529 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.9830 | 0.9630 |

![California Housing resize score](docs/figures/stable_partition_real.svg)

The mechanism ablation matters. Remapping labels from centroids loses badly against stable ancestor-label inheritance:

![Stable label ablation](docs/figures/stable_partition_ablation.svg)

This does not mean RDT is the fastest partitioner. In timing checks, grid and Morton ordering were faster. The current value is the measured tradeoff: lower movement than spatial orderings, much better locality than hash-only baselines, and acceptable load balance in the tested tasks.

### RDT-Cover

The RDT-cover benchmark generates numeric test inputs and counts predeclared edge-case classes. The seeded classes include zero boundary, large cancellation, power transition, outer corner, and thin annulus.

| Method | Mean bug classes found | Mean total hits |
|---|---:|---:|
| RDT full | 5.00 | 75.20 |
| RDT+Sobol | 5.00 | 70.20 |
| Powers-only | 4.00 | 89.40 |
| Midpoints-only | 3.00 | 63.00 |
| Boundaries-only | 3.00 | 40.00 |
| Random uniform | 2.00 | 35.60 |
| Sobol | 2.00 | 34.20 |

![RDT-cover edge-case discovery](docs/figures/coverage_ablation.svg)

This result supports RDT-cover as an edge-case complement to random and low-discrepancy sampling. It does not yet show superiority over property-based testing, fuzzing, Hypothesis strategies, or real numerical bug corpora.

### Residual Sampling Failure Case

The residual sampler is included because failures are useful. On the real California Housing residual field, greedy top-residual selection beats RDT-tuned selection:

![Residual sampler failure case](docs/figures/residual_real.svg)

That is why the residual sampler remains a research module. It needs full PDE/PINN training loops and RAR/RAD-style baselines before it can support any training claim.

## Installation

For local development:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
```

Public-data reruns use scikit-learn:

```bash
python -m pip install -e ".[test,data]"
```

## Quick Start

```python
import numpy as np
from rdt_adaptive_hierarchy import RDTStablePartition
from rdt_adaptive_hierarchy.core.metrics import movement_fraction

points = np.random.default_rng(0).random((1000, 2))
partitioner = RDTStablePartition(max_buckets=32).fit(points)

labels_16 = partitioner.assign_training(16)
labels_20 = partitioner.assign_training(20)

print(movement_fraction(labels_16, labels_20))
```

Expected output is a movement fraction near `0.125` for this small random example.

Run examples:

```bash
PYTHONPATH=src python examples/stable_partition_basic.py
PYTHONPATH=src python examples/cover_basic.py
PYTHONPATH=src python examples/geometry_validation_basic.py
PYTHONPATH=src python examples/residual_sampler_research_demo.py
```

## Benchmark Commands

Fast smoke runs:

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 2 --n 2000 --output-dir results/tmp/stable_partition
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 2 --budget 256 --output-dir results/tmp/cover
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.residual_sampler_bench --seeds 2 --n-side 48 --output-dir results/tmp/residual
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.geometry_bench --output-dir results/tmp/geometry
```

Tests:

```bash
PYTHONPATH=src pytest -q
```

Current local validation: `14 passed`.

## Repository Map

| Path | Purpose |
|---|---|
| `src/rdt_adaptive_hierarchy/core/` | Core cells, hierarchy, labels, metrics, coverage, refinement, validation. |
| `src/rdt_adaptive_hierarchy/applications/` | Stable partitioning, RDT-cover, residual sampler, geometry validation, shell diagnostics. |
| `src/rdt_adaptive_hierarchy/baselines/` | Jump Hash, rendezvous hashing, Morton ordering, grid, random, Sobol, Latin hypercube. |
| `src/rdt_adaptive_hierarchy/benchmarks/` | Runnable benchmark entry points. |
| `examples/` | Short scripts that show the public API. |
| `docs/` | Definitions, framework specification, claims, limitations, prior work, reproducibility. |
| `results/` | Interpreted summaries and raw benchmark artifacts. |
| `paper/` | Complete Markdown draft, references, and methods-paper notes. |

## What Is Not Claimed

This project does not claim that RDT is:

- a universal algorithm,
- a universal entropy theory,
- a cryptographic primitive,
- a turbulence or magnetohydrodynamics closure theory,
- a general compressor,
- a general anomaly detector,
- a replacement for all standard spatial indexes or testing tools.

Raw RDT spatial indexes are not promoted in this release. Prior adapters matched exactness, but did not establish speed superiority. The spatially useful claim here is stable partitioning under resize.

## Relation To Known Methods

The closest neighbors are consistent hashing, Jump Consistent Hash, rendezvous hashing, Morton/Z-order layouts, tree-based spatial indexes, geospatial hierarchies such as H3 and S2, property-based testing, quasi-Monte Carlo sampling, adaptive random testing, and residual adaptive refinement.

RDT should be compared against those methods before stronger public claims. Current missing baselines include Hilbert curves, H3, S2, geohash, virtual-node consistent hashing, Hypothesis, and real numerical bug corpora.

## Project Status

This is a pre-release research package. It is ready for technical review, reproduction, and focused development. It is not ready for broad claims of general superiority.

The best next development target is `rdt-stable-partition`, followed by `rdt-cover`. Residual sampling, shell drift, and codec-related ideas should stay experimental until they beat stronger baselines on real tasks.

## Citation

Use the metadata in [CITATION.cff](CITATION.cff). Until the method is published, cite this repository and the exact commit used.

## License

MIT. See [LICENSE](LICENSE).
