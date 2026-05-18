# Release Process

This file records the maintainer release process for `rdt-adaptive-hierarchy`.

Current package identity:

- Distribution name: `rdt-adaptive-hierarchy`
- Import name: `rdt_adaptive_hierarchy`
- Current version: `0.1.0`

The packaging flow follows the Python Packaging User Guide:

- Packaging tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- TestPyPI guide: https://packaging.python.org/en/latest/guides/using-testpypi/
- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/

## Version Policy

Use one version consistently across the package. If a future upload should be explicitly alpha, change all version references to an alpha version such as `0.1.1a1` before building:

- `pyproject.toml`
- `src/rdt_adaptive_hierarchy/__init__.py`
- `CITATION.cff`
- `README.md` package badge

Do not mix `0.1.0` and `0.1.0a1` in the same build.

## Local Build Check

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Expected artifacts:

```text
dist/rdt_adaptive_hierarchy-0.1.0-py3-none-any.whl
dist/rdt_adaptive_hierarchy-0.1.0.tar.gz
```

## Local Wheel Install Check

Use a clean virtual environment:

```bash
python -m venv /tmp/rdt-package-check
/tmp/rdt-package-check/bin/python -m pip install --upgrade pip
/tmp/rdt-package-check/bin/python -m pip install dist/rdt_adaptive_hierarchy-0.1.0-py3-none-any.whl
/tmp/rdt-package-check/bin/python -c "import rdt_adaptive_hierarchy; print(rdt_adaptive_hierarchy.__version__)"
/tmp/rdt-package-check/bin/python -c "from rdt_adaptive_hierarchy import RDTHierarchy, RDTStablePartition, rdt_cover"
```

## TestPyPI Upload

Manual token upload:

```bash
python -m twine upload --repository testpypi dist/*
```

When prompted, use username `__token__` and paste the TestPyPI API token as the password. Do not write tokens into this repository.

Then test installation from TestPyPI in a new environment:

```bash
python -m venv /tmp/rdt-testpypi-check
/tmp/rdt-testpypi-check/bin/python -m pip install --upgrade pip
/tmp/rdt-testpypi-check/bin/python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rdt-adaptive-hierarchy
/tmp/rdt-testpypi-check/bin/python -c "from rdt_adaptive_hierarchy import RDTHierarchy, RDTStablePartition, rdt_cover"
```

## PyPI Upload

Only after TestPyPI install succeeds:

```bash
python -m twine upload dist/*
```

Use username `__token__` and the real PyPI API token as the password.

## Trusted Publishing

The preferred long-term release path is PyPI Trusted Publishing through GitHub Actions. This repo includes a manual-only workflow at `.github/workflows/publish.yml`.

Before using it, configure the trusted publisher in PyPI/TestPyPI with:

- Owner: `RRG314`
- Repository: `RDT-Adaptive-Hierarchies`
- Workflow: `publish.yml`
- Environment: `testpypi` for TestPyPI or `pypi` for PyPI

The workflow is not triggered by push. It only runs through `workflow_dispatch`.

## Rollback and Yank Notes

PyPI files cannot be overwritten once uploaded. If a release has a serious issue:

1. Publish a fixed version with a higher version number.
2. Yank the bad release if users should avoid it.
3. Do not delete release records unless there is a compelling reason.

## Release Checklist

- `pytest -q` passes.
- Public examples run after package install.
- `python -m build` succeeds.
- `python -m twine check dist/*` passes.
- Wheel install works in a clean environment.
- Source distribution contains docs, figures, examples, tests, paper notes, and summary tables.
- Wheel excludes raw benchmark artifacts.
- README renders cleanly on PyPI.
- Claims remain bounded as a research pre-release.
- No PyPI tokens are committed.
