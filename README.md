# RDT Adaptive Hierarchies

[![CI](https://github.com/RRG314/RDT-Adaptive-Hierarchies/actions/workflows/ci.yml/badge.svg)](https://github.com/RRG314/RDT-Adaptive-Hierarchies/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Package](https://img.shields.io/badge/package-0.1.0-informational.svg)
![Status](https://img.shields.io/badge/status-research%20pre--release-orange.svg)

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
| Stable partitioning | In the deep validation run, RDT stable labels had the best combined movement/locality/load score in `40/40` dataset/resize tasks against hash, spatial-ordering, geospatial, grid, remapped-label, and null-control baselines. | Strongest current direction. The claim is a tradeoff claim, not raw speed superiority. |
| RDT-cover | On the expanded 14-class seeded corpus at budget `1024`, Hypothesis-targeted found `13/14` classes, powers-only found `11/14`, RDT-cover found `10/14`, and blind random/Sobol/Halton/Latin found `4/14`. | Useful deterministic edge-case generator, but narrower than before. Power/scale anchors explain much of the gain, and Hypothesis is stronger when predicates are known. |
| Geometry validation | Recursive-depth schedule still passes selected known-form checks, but Sobol/QMC dominates several simple integration tests. | Bounded numerical validation result, not a new geometry theory. |
| Residual sampling | RDT variants win on selected synthetic fields, but lose to greedy or stratified baselines on oscillatory, multi-front, and real California residual fields. | Research-only. No PDE/PINN training claim is supported. |
| Shell drift | Some synthetic shifts are detected, but simple histogram and mean/std baselines are competitive or better. | Diagnostic-only. Not an anomaly detector claim. |
| Recursive delta codec | Helps ramp-like synthetic bytes but loses to standard compressors on text and CSV corpora. | Narrow transform observation. Not a general compressor. |

## Headline Results

### Stable Partitioning

The stable partition benchmark resizes from `k1` buckets to `k2` buckets. Lower combined score is better:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

On California Housing coordinates (`n = 20,640`):

| Resize | RDT stable | Jump Hash | Morton sort | Principal sort |
|---|---:|---:|---:|---:|
| 16 -> 20 | 0.4686 | 0.6746 | 0.9208 | 0.8939 |
| 32 -> 40 | 0.4695 | 0.7174 | 0.9682 | 0.9531 |
| 64 -> 80 | 0.4706 | 0.7219 | 0.9889 | 0.9846 |
| 128 -> 160 | 0.4514 | 0.7544 | 0.9971 | 0.9991 |

![California Housing resize score](docs/figures/stable_partition_real.svg)

The mechanism ablation matters. Remapping labels from centroids loses badly against stable ancestor-label inheritance:

![Stable label ablation](docs/figures/stable_partition_ablation.svg)

This does not mean RDT is the fastest partitioner. In timing checks, grid and Morton ordering were faster. The current value is the measured tradeoff: lower movement than spatial orderings, much better locality than hash-only baselines, and acceptable load balance in the tested tasks.

The release-hardening benchmark adds Hilbert, H3, S2, geohash, and virtual-node consistent hashing on 5 synthetic seeds. RDT stable labels remain the best combined score in the tested uniform, clustered, and diagonal datasets:

| Dataset | RDT stable | Rendezvous | Jump Hash | Virtual-node hash | Best spatial ordering |
|---|---:|---:|---:|---:|---:|
| Uniform | 0.2005 ± 0.0003 | 0.6622 ± 0.0003 | 0.6757 ± 0.0001 | 0.7346 ± 0.0004 | Hilbert 0.9050 ± 0.0003 |
| Clustered | 0.2739 ± 0.0202 | 0.6628 ± 0.0002 | 0.6760 ± 0.0002 | 0.7347 ± 0.0002 | Morton 0.9012 ± 0.0014 |
| Diagonal | 0.1784 ± 0.0002 | 0.6627 ± 0.0004 | 0.6758 ± 0.0001 | 0.7346 ± 0.0004 | Principal sort 0.8771 ± 0.0000 |

Peak Python memory in that run was about `26,957 KiB`. This is process-level `tracemalloc` peak memory for the benchmark run, not a per-method resident-set-size profile.

### RDT-Cover

The RDT-cover benchmark generates numeric test inputs and counts predeclared edge-case classes. The expanded corpus now includes zero boundary, near-zero division, overflow-adjacent values, underflow-adjacent values, cancellation, powers of ten, powers of two, square-root and log-domain boundaries, trigonometric periodic boundaries, outer corners, thin annuli, near-singular matrices, and ill-conditioned vectors.

At budget `1024` on the deep-validation run:

| Method | Mean classes found | Mean total hits |
|---|---:|---:|
| Hypothesis-targeted | 13.00 | 1294.33 |
| Powers-only ablation | 11.00 | 661.33 |
| RDT full | 10.00 | 199.67 |
| Boundary-only ablation | 9.00 | 306.67 |
| RDT+Sobol | 9.00 | 256.33 |
| Random uniform | 4.00 | 278.33 |
| Sobol | 4.00 | 268.67 |
| Halton | 4.00 | 270.67 |
| Latin hypercube | 4.00 | 272.33 |

![RDT-cover edge-case discovery](docs/figures/coverage_ablation.svg)

This result supports RDT-cover as an edge-case complement to random and low-discrepancy sampling. It also narrows the claim. The powers-only ablation found more classes than full RDT-cover on this corpus, so power and scale anchors explain much of the useful behavior. Hypothesis-targeted coverage found the most classes because it uses predicate-aware strategies. The correct claim is therefore: RDT-cover is a deterministic multiscale schedule that can improve blind coverage, not a replacement for property-based testing or tuned edge-case strategies.

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

Full release-check dependencies include optional geospatial baselines, Hypothesis integration, memory profiling, package build tooling, and public-data support:

```bash
python -m pip install -e ".[dev]"
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
PYTHONPATH=src python examples/cover_hypothesis_basic.py
```

## Benchmark Commands

Fast smoke runs:

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 2 --n 2000 --output-dir results/tmp/stable_partition
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 2 --budgets 256 --output-dir results/tmp/cover
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.residual_sampler_bench --seeds 2 --n-side 48 --output-dir results/tmp/residual
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.geometry_bench --output-dir results/tmp/geometry
```

Tests:

```bash
PYTHONPATH=src pytest -q
```

Current local validation: `18 passed`.

GitHub Actions runs tests on Python 3.11 and 3.12, executes public examples, runs benchmark smoke checks, and builds source/wheel distributions.

## Repository Map

| Path | Purpose |
|---|---|
| `src/rdt_adaptive_hierarchy/core/` | Core cells, hierarchy, labels, metrics, coverage, refinement, validation. |
| `src/rdt_adaptive_hierarchy/applications/` | Stable partitioning, RDT-cover, residual sampler, geometry validation, shell diagnostics. |
| `src/rdt_adaptive_hierarchy/baselines/` | Jump Hash, virtual-node hashing, rendezvous hashing, Morton, Hilbert, H3, S2, geohash, grid, random, Sobol, Latin hypercube, Hypothesis-targeted coverage. |
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

Raw RDT spatial indexes are not the headline claim in this release. They live in the companion [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index) repository, which is the correct home for range-query and kNN-oriented indexing code. This repo uses that line of work as provenance and comparison context, while keeping the public claim here focused on stable partitioning under resize.

## Known Failure Cases

These are part of the release boundary, not footnotes:

- RDT is not the fastest raw partitioner. Grid, Morton, and other simple orderings can be faster in machine-local timing checks.
- RDT-cover is not better than targeted property-based testing when the failure predicates are known. In the deep-validation run, Hypothesis-targeted coverage found `13/14` seeded classes, while full RDT-cover found `10/14`.
- The RDT-cover ablation matters in both directions: power-only anchors found `11/14` classes, so the full schedule is not yet the best combination for the expanded synthetic corpus.
- RDT residual sampling is mixed. It helps selected synthetic hotspot fields but loses to greedy top-residual selection on a real California Housing residual field.
- Shell drift is diagnostic-only. Simple histogram and mean/std baselines remain competitive.
- Recursive delta preprocessing is not a general compressor. It helps ramp-like synthetic bytes and loses on real text/CSV corpora.
- Raw RDT spatial-index results are handled as companion-repo evidence, not as a claim that this package replaces mature spatial indexes.

## Relation To Known Methods

The closest neighbors are consistent hashing, Jump Consistent Hash, rendezvous hashing, Morton/Z-order layouts, tree-based spatial indexes, geospatial hierarchies such as H3 and S2, property-based testing, quasi-Monte Carlo sampling, adaptive random testing, and residual adaptive refinement. The closest internal companion project is [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index), which focuses on practical spatial indexing rather than stable resize partitioning.

RDT should be compared against those methods before stronger public claims. Hilbert, H3, S2, geohash, virtual-node consistent hashing, and Hypothesis-targeted coverage are now implemented. Remaining missing work includes larger real workloads, production-style tuning, full memory profiling, and real numerical bug corpora.

## Project Status

This is a pre-release research package. It is ready for technical review, reproduction, and focused development. It is not ready for broad claims of general superiority.

The best next development target is `rdt-stable-partition`, followed by `rdt-cover`. Residual sampling, shell drift, and codec-related ideas should stay experimental until they beat stronger baselines on real tasks.

## Citation

Use the metadata in [CITATION.cff](CITATION.cff). Until the method is published, cite this repository and the exact commit used.

## License

MIT. See [LICENSE](LICENSE).
