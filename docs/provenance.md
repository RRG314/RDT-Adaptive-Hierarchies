# Provenance

This repository is a cleaned package derived from earlier local RDT experiments and benchmark runs. Original notebooks, Google Drive files, extraction archives, and unrelated repositories are not part of this package.

## Active Code

| Current file | Source lineage | Status |
|---|---|---|
| `src/rdt_adaptive_hierarchy/core/hierarchy.py` | RDT competitive benchmark implementation, polished into the active hierarchy API | active |
| `src/rdt_adaptive_hierarchy/core/rdt_v1.py` | frozen RDT-v1 reference behavior | active reference |
| `src/rdt_adaptive_hierarchy/applications/stable_partition.py` | stable partition experiments promoted into package code | active |
| `src/rdt_adaptive_hierarchy/applications/cover.py` | deterministic coverage experiments promoted into package code | active |
| `src/rdt_adaptive_hierarchy/applications/residual_sampler.py` | residual sampling experiments | research-only |
| `src/rdt_adaptive_hierarchy/applications/geometry_validation.py` | recursive-depth geometry validation experiments | experimental |

## Result Artifacts

| Artifact | Command/source | Seed range |
|---|---|---|
| `results/raw/reproduce_deep_5seed_2026-05-18/` | `python -m rdt_adaptive_hierarchy.benchmarks.reproduce_evidence --seed 0 --seeds 5 --deep` before cleanup | 0..4 |
| `results/raw/ablation_5seed_2026-05-18/` | ablation benchmark before cleanup | 0..4 |
| `results/raw/artifact_performance_5seed_2026-05-18/` | artifact/performance benchmark before cleanup | 0..4 |
| `results/raw/real_public_data_2026-05-18/` | real public data benchmark before cleanup | seed 0 |
| `results/raw/geometry_validation_2026-05-18/` | geometry validation benchmark before cleanup | deterministic |

## Public Data Sources

| Dataset | Source | Use |
|---|---|---|
| California Housing | scikit-learn `fetch_california_housing` | real geospatial partition and residual field |
| NAB ambient temperature | Numenta Anomaly Benchmark | drift diagnostic and CSV corpus |
| Project Gutenberg Alice | Project Gutenberg ebook 11 | text compression corpus |

Downloaded cache files are intentionally not tracked. Rerun commands should fetch public data as needed.
