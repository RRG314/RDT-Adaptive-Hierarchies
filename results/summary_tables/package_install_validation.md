# Package Install Validation

Validation date: 2026-05-18

Package artifact tested:

- `dist/rdt_adaptive_hierarchy-0.1.0-py3-none-any.whl`
- `dist/rdt_adaptive_hierarchy-0.1.0.tar.gz`

## Development Install

| Command | Result |
|---|---|
| `uv pip install --python .venv/bin/python -e ".[dev]"` | PASS |
| `.venv/bin/python -m pytest -q` | PASS, `23 passed` |

## Examples From Editable Install

| Command | Result |
|---|---|
| `.venv/bin/python examples/stable_partition_basic.py` | PASS, movement `0.125`, locality `0.0561`, labels `20` |
| `.venv/bin/python examples/cover_basic.py` | PASS, `256` points, `9` bug classes found |
| `.venv/bin/python examples/geometry_validation_basic.py` | PASS, RDT max relative error `0.00036741` |
| `.venv/bin/python examples/residual_sampler_research_demo.py` | PASS, research-only demo, composite score `0.6452` |
| `.venv/bin/python examples/cover_hypothesis_basic.py` | PASS, found cancellation example `(-10000.0, 10000.0)` |

## Build and README Check

| Command | Result |
|---|---|
| `.venv/bin/python -m build` | PASS |
| `.venv/bin/python -m twine check dist/*` | PASS for wheel and source distribution |

## Clean Basic Wheel Install

Environment:

- Python: CPython `3.12.12`
- Virtual environment: temporary `/tmp/rdt-basic-*`
- Install command: `uv pip install --python <env>/bin/python dist/rdt_adaptive_hierarchy-0.1.0-py3-none-any.whl`

| Check | Result |
|---|---|
| `import rdt_adaptive_hierarchy; print(rdt_adaptive_hierarchy.__version__)` | PASS, printed `0.1.0` |
| `from rdt_adaptive_hierarchy import RDTHierarchy, RDTStablePartition, rdt_cover, rdt_hybrid_cover, movement_fraction, load_imbalance, locality_dispersion` | PASS |
| `python examples/stable_partition_basic.py` | PASS |
| `python examples/cover_basic.py` | PASS |
| `rdt-stable-partition-bench --help` | PASS |
| `rdt-cover-bench --help` | PASS |

## Clean Optional Wheel Install

Environment:

- Python: CPython `3.12.12`
- Virtual environment: temporary `/tmp/rdt-optional-*`
- Install command: `uv pip install --python <env>/bin/python "<wheel>[test,data,baselines,profile]"`

Installed optional dependency groups:

- `test`
- `data`
- `baselines`
- `profile`

| Check | Result |
|---|---|
| `python examples/cover_hypothesis_basic.py` | PASS |
| `python -m rdt_adaptive_hierarchy.benchmarks.stable_partition_bench --seeds 1 --n 1000 --output-dir results/tmp/package_check_stable` | PASS |
| `python -m rdt_adaptive_hierarchy.benchmarks.cover_bench --seeds 1 --budgets 128 --output-dir results/tmp/package_check_cover` | PASS |

## Artifact Contents

| Artifact | Result |
|---|---|
| Wheel | PASS, contains importable package and entry points only |
| Source distribution | PASS, contains docs, figures, examples, tests, paper notes, and summary tables |
| Raw benchmark artifacts | PASS, excluded from wheel and source distribution |
| Temporary benchmark outputs | PASS, excluded from wheel and source distribution |

## Notes

- The first editable install attempt using `.venv/bin/python -m pip` failed because the existing local `.venv` did not expose `pip` as a module. The package itself was not at fault. Validation continued with `uv pip install --python .venv/bin/python`.
- Latest setuptools rejected the legacy MIT license classifier when `license = "MIT"` was present. The classifier was removed and the build backend was set to `setuptools>=77`, matching current license-expression behavior.

