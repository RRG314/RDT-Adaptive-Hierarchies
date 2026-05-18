# Overview

RDT began as a recursive depth idea explored across notebooks, experiments, and prototype repos. Those experiments tested many possible uses: random number generation, physics diagnostics, compression, geometry, spatial indexing, retrieval, and more. The broadest claims did not survive careful benchmarking.

The useful part that remains is smaller and more concrete. RDT works best here as a deterministic recursive hierarchy with metadata: depth, shell, ancestors, descendants, paths, and stable labels. That hierarchy is useful when we can measure a specific tradeoff.

The strongest tradeoff is stable partitioning. When the number of buckets changes, one goal is to move as few points as possible. Another goal is to keep nearby points together. Hashing methods are good at movement. Spatial orderings and grids are good at locality. RDT stable partitioning sits between those goals by preserving ancestor labels during recursive refinement.

The second strong use is coverage. RDT-cover is a deterministic case generator for numerical testing. It intentionally places cases at boundaries, midpoints, powers of ten, and shell-like scale transitions. That makes it useful for finding finite-budget edge cases that random and low-discrepancy samples can miss.

This repo formalizes that smaller version. It does not preserve every previous RDT application as a claim. Residual sampling is kept as research-only. Shell drift is diagnostic-only. Recursive-depth geometry validation is bounded to known-form numerical checks. Broad entropy, crypto, physics, biology, language, and general compression claims are outside the project.

## What To Read First

1. `README.md` for the project in plain language.
2. `docs/framework_specification.md` for the formal objects and operations.
3. `docs/claims_and_evidence.md` for supported and unsupported claims.
4. `docs/benchmark_interpretation.md` for the current result readout.
5. `docs/reproducibility.md` for commands and artifacts.

