# Reproducibility

## Environment

Create a local environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test,data]"
```

For release checks with optional baselines and package build tooling:

```bash
python -m pip install -e ".[dev]"
```

The latest local submission-validation run used:

- Python `3.12.12`
- NumPy `2.4.5`
- SciPy `1.17.1`
- scikit-learn `1.8.0`
- pytest `9.0.3`
- Hypothesis `6.152.7`
- h3 `4.4.2`
- s2sphere `0.2.5`
- pygeohash `3.2.2`
- psutil `7.2.2`

## Unit Tests

```bash
PYTHONPATH=src pytest -q
```

Expected current result: all tests pass.

## Examples

```bash
PYTHONPATH=src python examples/stable_partition_basic.py
PYTHONPATH=src python examples/cover_basic.py
PYTHONPATH=src python examples/geometry_validation_basic.py
PYTHONPATH=src python examples/residual_sampler_research_demo.py
PYTHONPATH=src python examples/cover_hypothesis_basic.py
```

## Benchmark Smoke Runs

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --output-dir results/tmp/stable_partition --seeds 2 --n 2000
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --output-dir results/tmp/cover --seeds 2 --budgets 256
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.residual_sampler_bench --output-dir results/tmp/residual_sampler --seeds 2 --n-side 48
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.geometry_bench --output-dir results/tmp/geometry
```

The stable partition smoke run includes Hilbert and virtual-node consistent hashing by default. If optional packages are installed, it also includes H3, S2, and geohash. The cover benchmark includes Hypothesis-targeted coverage when `hypothesis` is installed.

## Submission-Validation Snapshot

The latest submission-validation artifacts were generated on 2026-05-18 with these commands:

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 10 --n 3000 --datasets uniform,clustered,diagonal,hotspot_tail,anisotropic_gaussian,ring_annulus,two_clusters_imbalance,california_housing,us_cities,digits_pca2,digits_64d,breast_cancer_features --resize-pairs 8:10,16:20,32:40,64:80,128:160 --geospatial-baselines geospatial --rendezvous-baseline off --output-dir results/raw/submission_validation_2026-05-18/stable_partition

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 10 --n 3000 --datasets california_housing,us_cities --resize-pairs 8:10,16:20,32:40,64:80,128:160 --geospatial-baselines geospatial --rendezvous-baseline on --output-dir results/raw/submission_validation_2026-05-18/stable_partition_full_geospatial_baselines

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 10 --budgets 128,256,512,1024,2048 --output-dir results/raw/submission_validation_2026-05-18/cover

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_property_bench --seeds 10 --budget 512 --output-dir results/raw/submission_validation_2026-05-18/cover_property

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.performance_scaling --stable-sizes 1000,5000,20000,50000 --cover-budgets 128,512,1024,2048 --output-dir results/raw/submission_validation_2026-05-18/performance_scaling
```

These runs report 95% confidence intervals where repeated seeds are used. Memory reports include Python `tracemalloc` peak memory and process resident-set-size snapshots through `psutil` when available. They are not isolated per-method memory profiles.

## Release-Hardening Snapshot

The latest release-hardening artifacts were generated with:

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 5 --n 5000 --output-dir results/raw/release_hardening_2026-05-18/stable_partition
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 5 --budgets 512 --output-dir results/raw/release_hardening_2026-05-18/cover
```

These older runs report 95% confidence intervals and Python `tracemalloc` peak memory. They are retained as historical release-hardening artifacts.

## Deep-Validation Snapshot

The latest deep-validation artifacts were generated on 2026-05-18 with these commands:

```bash
PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 3 --n 3000 --datasets uniform,clustered,diagonal,hotspot_tail,anisotropic_gaussian,ring_annulus,two_clusters_imbalance,california_housing --resize-pairs 8:10,16:20,32:40,64:80,128:160 --output-dir results/raw/deep_validation_2026-05-18/stable_partition

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 3 --budgets 128,256,512,1024 --output-dir results/raw/deep_validation_2026-05-18/cover

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.residual_sampler_bench --seeds 3 --n-side 56 --output-dir results/raw/deep_validation_2026-05-18/residual_sampler

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.geometry_bench --output-dir results/raw/deep_validation_2026-05-18/geometry

PYTHONPATH=src python -m rdt_adaptive_hierarchy.benchmarks.performance_scaling --stable-sizes 1000,5000,20000,50000 --cover-budgets 128,256,512,1024,2048 --output-dir results/raw/deep_validation_2026-05-18/performance_scaling
```

Those runs are retained for residual sampling and geometry validation context. The stable partition, RDT-cover, and performance summaries now use the newer submission-validation artifacts.

## Datasets

The checked-in raw results reference:

- synthetic spatial datasets generated from fixed seeds,
- seeded numerical edge-case predicates,
- property-style floating-point checks,
- synthetic residual fields,
- California Housing from scikit-learn,
- sklearn digits and breast-cancer datasets,
- public US cities latitude/longitude points from Plotly's datasets repository,
- Numenta Anomaly Benchmark ambient temperature data,
- Project Gutenberg Alice text.

Downloaded data caches are not tracked. Active benchmark code downloads or generates data when needed.

## Raw Results

Raw benchmark artifacts live in `results/raw/`. They include JSON, CSV, and Markdown result cards from the formalization run. Summary files in `results/summary_tables/` interpret those artifacts.

## Seeds

The submission-validation run uses seeds `0..9` where repeated trials were used. Older release-hardening artifacts use seeds `0..4`; older deep-validation artifacts use seeds `0..2`. The public smoke commands default to smaller runs so a reviewer can verify the code quickly.

## Verification Checklist

1. Run unit tests.
2. Run examples.
3. Run benchmark smoke commands.
4. Compare output files with the summary tables.
5. Check `docs/claims_and_evidence.md` before using any result in public writing.
