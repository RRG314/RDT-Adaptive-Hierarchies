# Examples

Run examples from the repository root:

```bash
PYTHONPATH=src python examples/stable_partition_basic.py
PYTHONPATH=src python examples/cover_basic.py
PYTHONPATH=src python examples/cover_hypothesis_basic.py
PYTHONPATH=src python examples/geometry_validation_basic.py
PYTHONPATH=src python examples/residual_sampler_research_demo.py
```

`stable_partition_basic.py` builds an RDT hierarchy over random points and reports movement from 16 to 20 buckets.

`cover_basic.py` generates RDT+Sobol numerical coverage points and reports which seeded edge-case classes were found.

`cover_hypothesis_basic.py` shows the optional Hypothesis integration by finding a large-cancellation example from an edge-aware numeric strategy.

`geometry_validation_basic.py` runs the known-form geometry validator for radius `1.0`.

`residual_sampler_research_demo.py` demonstrates the research-only residual sampler on a synthetic two-hotspot field. It is included to make the experimental module inspectable, not to claim PDE training improvement.
