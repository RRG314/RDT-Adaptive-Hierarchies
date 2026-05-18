# RDT Adaptive Hierarchies

RDT Adaptive Hierarchies is a small research/software project for deterministic recursive partitions. It focuses on a specific idea: a hierarchy can carry useful metadata, especially stable labels, ancestor paths, depth/shell information, and coverage schedules. Those pieces can be measured directly with movement, locality, load balance, and edge-case discovery tests.

This repository is not a continuation of every earlier RDT notebook idea. Earlier experiments made much broader claims. The evidence here supports a smaller and more useful project: stability-preserving partitioning and multiscale coverage.

## The Problem

Many systems need to resize or refine a partition without moving everything. Hashing methods can minimize movement, but they usually discard locality. Space-filling curves and grids preserve locality, but they can move many points when the number of buckets changes. RDT stable partitioning studies the tradeoff between those goals.

Numerical testing has a related problem. Pure random and low-discrepancy sampling can fill a space evenly, but they may miss specific boundary, scale, or cancellation cases. RDT-cover adds deterministic boundary, midpoint, power-scale, and shell-oriented cases as a complement to standard sampling.

## What RDT Means Here

In this repo, RDT means a deterministic recursive hierarchy:

- points are recursively split into cells,
- each cell has a depth and ancestor path,
- active cells receive stable labels,
- when a cell splits, one child inherits the parent label,
- coverage schedules can target boundaries, midpoints, powers, and shells.

The most important mechanism is stable ancestor-label inheritance. Recursion by itself is not the claim.

## What Is Supported

Current evidence supports these bounded statements:

- Stable labels improve the movement/locality/load tradeoff in the tested resize tasks.
- RDT-cover finds seeded numerical edge-case classes that random, Sobol, and Latin hypercube miss in the current benchmark.
- Recursive-depth geometry validation can reproduce selected known forms with low error.
- Residual sampling is mixed and remains research-only.
- Shell drift is diagnostic-only.
- Recursive delta preprocessing is a narrow observation for ramp-like byte sequences, not an active package module.

## What Is Not Claimed

This project does not claim that RDT is:

- a universal algorithm,
- a universal entropy theory,
- a cryptographic primitive,
- a turbulence or magnetohydrodynamics closure theory,
- a general compressor,
- a general anomaly detector,
- a replacement for all standard spatial indexes or testing tools.

Raw RDT spatial index adapters are not promoted as part of this release. They matched exactness in prior tests, but did not show speed superiority. The spatially useful claim in this repo is stable partitioning under resize.

## Installation

For local development:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
```

The core package depends on NumPy and SciPy. Public-data reruns may also need scikit-learn:

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

Run the examples:

```bash
PYTHONPATH=src python examples/stable_partition_basic.py
PYTHONPATH=src python examples/cover_basic.py
PYTHONPATH=src python examples/geometry_validation_basic.py
```

## Main Applications

`rdt-stable-partition` is the main supported application. It builds a recursive hierarchy and replays split history to assign stable labels during resize.

`rdt-cover` generates deterministic numeric test cases that emphasize boundaries, midpoints, powers of ten, and shell-like scale transitions. It is meant to complement, not replace, property-based testing and low-discrepancy sampling.

`recursive-depth geometry validation` is included as a bounded experimental module. It validates known forms; it does not assert a new geometry theory.

`rdt-residual-sampler` is research-only. It is useful for studying coverage-preserving residual selection, but current evidence does not support a broad PDE or PINN training claim.

## Benchmark Summary

The strongest current result is stable partitioning. On synthetic and California Housing coordinate resize tasks, RDT stable labels produce a better movement/locality/load score than the tested hashing and ordering baselines. Raw runtime is not always fastest; grid and Morton baselines are faster in timing checks.

RDT-cover found all five seeded numerical edge-case classes in the current benchmark. Random, Sobol, and Latin hypercube found two. This is useful evidence, but it is still a seeded corpus. Real bug corpora and Hypothesis integration remain open work.

See:

- [docs/benchmark_interpretation.md](docs/benchmark_interpretation.md)
- [results/README.md](results/README.md)
- [results/summary_tables/stable_partition_summary.md](results/summary_tables/stable_partition_summary.md)
- [results/summary_tables/cover_summary.md](results/summary_tables/cover_summary.md)

## Reproducibility

The repo includes raw benchmark artifacts from the current run under `results/raw/`, concise summaries under `results/summary_tables/`, and rerun commands in [docs/reproducibility.md](docs/reproducibility.md).

Core checks:

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench
```

## Relation To Known Methods

The closest neighbors are consistent hashing, Jump Consistent Hash, rendezvous hashing, Morton/Z-order layouts, geospatial hierarchies such as H3 and S2, tree-based spatial indexes, property-based testing, quasi-Monte Carlo sampling, adaptive random testing, and residual adaptive refinement.

RDT should be compared against those methods before making stronger public claims. See [docs/relation_to_prior_work.md](docs/relation_to_prior_work.md).

## Project Status

This is a pre-release research repository. It is suitable for technical review, reproduction, and focused development. It is not yet ready for a broad paper claim. The next serious work is stronger external baselines: Hilbert/H3/S2/geohash for stable partitioning and Hypothesis/real bug corpora for RDT-cover.

## Citation

Use the metadata in [CITATION.cff](CITATION.cff). Until the method is published, cite this repository and the exact commit used.

## License

MIT. See [LICENSE](LICENSE).

