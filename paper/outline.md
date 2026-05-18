# Paper Outline

Working title:

RDT Adaptive Hierarchies for Stability-Preserving Partitioning and Multiscale Coverage

## Thesis

A deterministic recursive hierarchy with stable ancestor-label inheritance can provide a useful movement/locality/load tradeoff during partition resize. The same hierarchy idea can also generate deterministic multiscale numerical test cases.

## Proposed Structure

1. Introduction: resizing and coverage problems.
2. Definitions: recursive cell, hierarchy, stable label, movement, locality, coverage.
3. Method: RDT-v1 construction and stable label replay.
4. Method: RDT-cover boundary, midpoint, power, and shell schedule.
5. Propositions: determinism, label inheritance, movement decomposition, enumerated coverage.
6. Experiments: stable partition synthetic and California Housing.
7. Experiments: RDT-cover seeded numeric corpus.
8. Ablations: stable labels vs remapping; cover components.
9. Failure cases: residual sampler, shell drift, codec, raw spatial index.
10. Limitations and future baselines.

## Paper Claim Boundary

The paper should not claim a universal RDT theory. It should be a bounded methods paper.

