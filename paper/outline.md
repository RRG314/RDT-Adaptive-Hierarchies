# Paper Draft Plan

Working title:

**RDT Adaptive Hierarchies for Stability-Preserving Partitioning and Multiscale Numerical Coverage**

This is not a complete manuscript yet. It records the paper-sized claim, the evidence available now, the experiments still missing, and the boundaries that must stay in the manuscript.

## One-Sentence Thesis

A deterministic recursive hierarchy with stable ancestor-label inheritance can provide a useful movement/locality/load tradeoff during partition resize, and the same hierarchy can generate deterministic edge-focused numerical coverage cases that complement random and low-discrepancy sampling.

## Abstract Draft

Partitioned systems often need to change the number of buckets without moving most assigned points. Hash-based methods can reduce movement, but they typically ignore geometric locality. Spatial orderings and grids preserve locality, but they may move many points or produce load imbalance during resize. This work studies RDT Adaptive Hierarchies, a deterministic recursive hierarchy that carries depth, path, and stable-label metadata. The central mechanism is ancestor-label inheritance: when a cell splits, one child keeps the parent label and the new branch receives a new label.

We evaluate the method on synthetic point sets and California Housing coordinates using a combined movement/locality/load score. In the current benchmark, stable RDT labels outperform Jump Hash, rendezvous hashing, Morton ordering, grid partitioning, principal sorting, modulo hashing, and a remapped-label ablation on the tested resize tasks. We also introduce RDT-cover, a deterministic numerical coverage schedule that targets boundaries, midpoints, powers of ten, corners, and shell-like scale transitions. In a seeded numerical edge-case benchmark, full RDT-cover and RDT+Sobol find all five predefined edge-case classes, while random, Sobol, and Latin hypercube find two.

The paper should make bounded claims only. RDT is not presented as a universal algorithm, a cryptographic primitive, a general compressor, or a replacement for mature spatial indexing systems. Residual sampling, shell drift, and recursive delta preprocessing are included only as limitations and research directions.

## Intended Contributions

1. Define RDT Adaptive Hierarchies as a deterministic recursive hierarchy with cells, depth, paths, stable labels, resize, refinement, and coverage operations.
2. Introduce stable ancestor-label inheritance as a concrete mechanism for reducing movement during partition resize while retaining locality information.
3. Provide a stable partition benchmark that reports movement, locality, load imbalance, combined score, and runtime against hashing and spatial-ordering baselines.
4. Provide RDT-cover as a deterministic edge-case coverage schedule for numerical test generation.
5. Report ablations that separate recursion from stable label inheritance and separate RDT-cover components.
6. Report failure cases where RDT should not be promoted: residual sampling on real residuals, shell drift versus simple baselines, codec behavior on real text/CSV data, and raw spatial-index speed.

## Claim Boundary

Allowed claims:

- Stable labels improve the tested movement/locality/load tradeoff.
- The ablation supports ancestor-label inheritance as the important mechanism.
- RDT-cover improves discovery of the seeded numerical edge-case classes in the current benchmark.
- Geometry validation is a bounded numerical check against known forms.

Forbidden claims:

- RDT is generally better than all consistent hashing or spatial indexing methods.
- RDT-cover is generally better than Hypothesis, fuzzing, or adaptive random testing.
- RDT is a universal entropy theory, cryptographic primitive, physics closure model, general compressor, or anomaly detector.

## Proposed Paper Structure

### 1. Introduction

Motivate two practical problems:

- Resizing partitions while controlling movement, locality, and load.
- Generating finite-budget numerical test cases that include edge and scale cases.

The introduction should explicitly say that this paper is not about all historical RDT experiments. It studies one narrowed framework and two supported applications.

### 2. Related Work

Required comparison areas:

- Consistent hashing and Jump Consistent Hash.
- Rendezvous/highest-random-weight hashing.
- Morton/Z-order and Hilbert spatial orderings.
- H3, S2, geohash, KDTree, quadtree, R-tree, and BVH as spatial hierarchy context.
- Sobol, Halton, Latin hypercube, quasi-Monte Carlo, adaptive random testing, and property-based testing.
- Residual adaptive refinement only as background for why residual sampling is not yet a supported claim.

### 3. Definitions

Define:

- data domain `X`,
- recursive cell,
- root, child, ancestor, descendant,
- depth and shell,
- active partition,
- stable label,
- recursive path,
- resize operation,
- movement cost,
- locality cost,
- load imbalance,
- coverage schedule,
- edge-case class.

The definitions should use small diagrams and examples before formal notation.

### 4. RDT-v1 Hierarchy Construction

Describe the reference implementation:

1. Start with the root cell.
2. Score active cells by `cell_size * max_coordinate_spread`.
3. Split the highest-scoring cell.
4. Choose the split dimension with maximum spread.
5. Split by deterministic median partition.
6. Repeat until the maximum leaf count or stopping rule is reached.

State limitations: the splitter is intentionally simple and should not be treated as an optimal tree builder.

### 5. Stable Partitioning

Describe stable label replay and resize:

- For `k` buckets, replay the first `k - 1` splits.
- When a labeled cell splits, the left child inherits the parent label and the right child receives the next unused label.
- Compare labels before and after resize.

Primary metrics:

- movement fraction,
- locality cost,
- load imbalance,
- combined score,
- build and assignment time.

Current key result on California Housing:

| Resize | RDT stable | Jump Hash | Morton sort |
|---|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.9195 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.9674 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.9830 |

### 6. RDT-Cover

Define the coverage schedule:

- center point,
- boundaries,
- zero if in domain,
- powers of ten and negatives,
- recursive midpoints,
- corners,
- shell-like jitter,
- optional Sobol fill.

Current key result:

| Method | Mean edge-case classes found |
|---|---:|
| RDT full | 5.00 |
| RDT+Sobol | 5.00 |
| Powers-only | 4.00 |
| Random uniform | 2.00 |
| Sobol | 2.00 |

The paper must say this is a seeded numerical corpus, not real bug-corpus evidence.

### 7. Ablations

Required ablations:

- Stable labels versus remapped labels.
- RDT stable labels versus Jump Hash and Morton.
- RDT-cover full versus boundaries-only, midpoints-only, powers-only, random, Sobol, and hybrid.
- Residual sampler full versus no-coverage, no-gradient, tuned, and greedy residual, presented as a limitation.

### 8. Failure Cases And Non-Claims

This section is important. It prevents the paper from sounding broader than the evidence.

Current failure/limitation cases:

- RDT is not fastest in raw partition timing.
- Residual sampler loses to top residual on real California residuals.
- Shell drift does not beat simple baselines consistently.
- Recursive delta preprocessing is not a general compressor.
- Raw RDT spatial index wrappers are not promoted because exactness did not become speed superiority.

### 9. Reproducibility Package

Describe:

- package installation,
- tests,
- benchmark commands,
- seeds,
- result artifact format,
- public datasets,
- raw and summary result locations.

### 10. Discussion

Explain the likely useful abstraction:

RDT is useful when hierarchy metadata lets the system preserve or target something measurable: labels during resize, scale/boundary cases during coverage, or known-form refinement schedules. It is not useful merely because a recursive partition can be inserted into a problem.

## Missing Before Submission

- Hilbert, H3, S2, geohash, and virtual-node consistent hashing baselines.
- Larger and more varied real partition workloads.
- Hypothesis and adaptive random testing comparisons for RDT-cover.
- Real numerical bug or mutant corpus for coverage.
- Runtime and memory scaling at larger `n`.
- Confidence intervals in the polished result tables.
- A clearer theory section for when stable label inheritance should or should not help.
