# RDT Adaptive Hierarchies for Stability-Preserving Partitioning and Multiscale Numerical Coverage

Steven Reid  
Independent Researcher  

## Abstract

Recursive Division Tree (RDT) began as an integer-depth construction for measuring recursive structure in the positive integers. The original RDT preprint introduced a log-log depth perspective on integer complexity and motivated later experiments with depth, shell, and recursive refinement metadata [1]. This paper narrows that broader research line into a more testable computational framework: **RDT Adaptive Hierarchies**, deterministic recursive hierarchies with cells, depth metadata, ancestor paths, stable labels, resize operations, refinement operations, and coverage schedules.

The central claim is intentionally bounded. RDT is useful when recursive hierarchy metadata preserves or targets a measurable property. The strongest current mechanism is **stable ancestor-label inheritance**: when a partition cell splits during resize, one child inherits the parent label and only the new branch receives a new label. This mechanism is evaluated on synthetic point sets and California Housing coordinates using movement, locality, load imbalance, and a combined movement/locality/load score. In the current benchmark, RDT stable labels outperform Jump Hash, rendezvous hashing, Morton ordering, grid partitioning, principal-axis sorting, modulo hashing, and a remapped-label ablation on the tested resize tasks. On California Housing coordinates, RDT stable labels score `0.4386`, `0.4945`, and `0.4641` on the `16 -> 20`, `32 -> 40`, and `64 -> 80` resize tasks, respectively, compared with Jump Hash scores of `0.6583`, `0.6664`, and `0.6790`.

The second supported application is **RDT-cover**, a deterministic numerical coverage schedule that targets boundaries, midpoints, powers of ten, corners, and shell-like scale transitions. In a seeded numerical edge-case benchmark, full RDT-cover and RDT+Sobol find all five predefined edge-case classes, while random uniform, Sobol, and Latin hypercube sampling find two at the tested budget. The result supports RDT-cover as a deterministic complement to random and low-discrepancy sampling, not as a replacement for property-based testing or fuzzing.

The paper also reports negative and mixed evidence. RDT is not the fastest raw partitioner in timing checks. RDT residual sampling loses to greedy top-residual selection on a real California Housing residual field. Shell drift is diagnostic-only. Recursive delta preprocessing helps ramp-like synthetic byte sequences but is not a general compressor. These limitations are part of the contribution: they separate a small, reproducible framework from broader unsupported RDT claims.

## Keywords

recursive hierarchy; stable partitioning; consistent hashing; numerical coverage; adaptive refinement; multiscale diagnostics; reproducible benchmarks

## 1. Introduction

Many computational systems use partitions that must change over time. A distributed service may add shards. A geospatial or vector system may change the number of active regions. A batch-processing pipeline may rebalance work across a new number of workers. In each case, one goal is to avoid moving everything. Another goal is to preserve locality or semantic neighborhood structure. These goals are often in tension.

Hash-based assignment methods can reduce movement when the number of buckets changes, but they generally do not preserve spatial locality. Spatial grids and ordering methods can group nearby points, but they may move many points or produce load imbalance during resize. The question addressed here is whether a deterministic recursive hierarchy can provide a useful intermediate point in this design space.

This paper studies **RDT Adaptive Hierarchies**, a narrowed computational form of Recursive Division Tree. The framework builds a deterministic binary hierarchy over numeric points. Cells have depths, parent-child relationships, paths, and stable labels. The main supported operation is resize: the hierarchy replays a deterministic split history to produce `k` active cells. When a labeled cell splits, one child inherits the parent label and the other child receives a new label. This rule is called stable ancestor-label inheritance.

The paper also studies a second application: deterministic numerical coverage. RDT-cover generates cases at domain boundaries, midpoints, powers of ten, corners, and shell-like scale transitions. The motivation is that random and low-discrepancy sampling can fill a domain well while still missing specific edge cases under a finite budget.

The contribution is deliberately smaller than the full historical RDT research program. Earlier notebooks and prototypes applied RDT-like ideas to integer depth, entropy diagnostics, spatial indexing, compression, weather features, physics diagnostics, retrieval, random number generation, and other domains. Systematic review and benchmarking weakened broad claims. The present paper keeps only the parts that can be defined, implemented, ablated, benchmarked, and falsified.

The resulting thesis is:

> RDT is useful when a recursive hierarchy preserves or targets a measurable property: stable labels during resize, scale and boundary cases during coverage, or bounded known-form validation. It is not useful merely because a recursive partition can be inserted into a problem.

## 2. Origin and Scope

The term Recursive Division Tree comes from earlier work on integer depth. The Zenodo preprint **Recursive Division Tree: A Log-Log Algorithm for Integer Depth** introduced RDT as a recursive depth method for positive integers and framed the depth as a way to examine structure across integer scales [1]. That work focused on integer-depth behavior, arithmetic structure, and empirical growth patterns.

The present repository and paper are not a direct continuation of every claim in that preprint. They are a software and benchmarking distillation that grew out of the same organizing idea: recursive division produces depth and shell metadata, and those metadata may be useful when they are measured against a baseline.

The shift from the earlier preprint to this framework has three important changes.

First, the domain changes. The original RDT work focused on positive integers and recursive integer depth. This framework operates primarily on finite numeric point sets and bounded numerical domains.

Second, the claim changes. The earlier research asked what recursive depth reveals about integer structure. This paper asks whether recursive hierarchy metadata improves specific computational tasks.

Third, the evidence standard changes. A claim is kept only when it has a definition, implementation, baseline comparison, ablation, metric, and failure condition.

Local notebook and repo consolidation identified several RDT-related branches after the preprint: recursive-depth integration notebooks, RDT transforms, RDT entropy diagnostics, RDT spatial indexing experiments, RDT weather features, and RDT/RGE randomness experiments. Most are not promoted here. They remain useful as provenance and negative evidence, but this paper focuses on stable partitioning and deterministic coverage because those are the clearest supported applications.

## 3. Related Work

### 3.1 Consistent Hashing and Stable Assignment

Consistent hashing addresses stable assignment of keys to buckets under membership changes. Jump Consistent Hash provides a compact method for mapping keys to buckets with low movement and minimal memory [2]. Rendezvous hashing, also known as highest-random-weight hashing, assigns each key to the bucket with the highest score and is a standard stable assignment baseline [3].

RDT stable partitioning shares the movement objective but differs by measuring spatial locality and load imbalance at the same time. Hashing baselines are strong movement baselines, but their locality behavior is weak when the input points have geometry.

### 3.2 Spatial Orderings and Hierarchical Indexes

Morton/Z-order mappings and Hilbert curves map multidimensional data into one-dimensional orderings that tend to preserve locality. Tree-based spatial indexes such as KD-trees, quadtrees, octrees, R-trees, and bounding volume hierarchies organize space hierarchically for search or geometry tasks. Geospatial systems such as H3 and S2 provide mature hierarchical cell systems over the Earth [4, 5].

RDT-v1 is not promoted as a replacement for those systems. The current implementation is evaluated as a stable resize partitioner, not as a range-query or nearest-neighbor index. The missing baseline list includes Hilbert curves, H3, S2, geohash, and production-style virtual-node hashing.

### 3.3 Numerical Coverage and Testing

Sobol and Halton sequences are standard low-discrepancy sequences used in quasi-Monte Carlo sampling [6]. Latin hypercube sampling stratifies each dimension. Property-based testing frameworks such as Hypothesis generate examples from user-defined strategies [7]. Adaptive random testing aims to spread generated tests to improve failure discovery [8].

RDT-cover is related but narrower. It does not optimize discrepancy alone. It intentionally spends budget on boundary, midpoint, power, and shell-like anchors. The benchmark therefore evaluates edge-case class discovery rather than only fill quality.

### 3.4 Adaptive Refinement and Residual Sampling

Adaptive mesh refinement and residual-based adaptive refinement refine computation where estimated error is high. In physics-informed neural networks, residual adaptive sampling methods such as RAR and RAD choose training points based on residual behavior [9]. RDT residual sampling is included in the repository only as research-only code because current evidence is mixed and no full PDE/PINN training claim is supported.

## 4. Definitions

Let `X` be a finite numeric dataset with shape `(n, d)`, where `n` is the number of points and `d` is the number of coordinate dimensions.

A **cell** is a node in a rooted binary tree. A cell stores:

- a cell identifier,
- an optional parent identifier,
- depth,
- point indices,
- optional split dimension,
- optional split threshold,
- optional left and right child identifiers.

The **root cell** contains all points. A **leaf cell** is a cell with no children. An **active partition** is a set of active leaf cells selected by replaying a prefix of the split history.

The **depth** of the root is `0`. The depth of a child is one plus the depth of its parent. In this release, **shell** is equivalent to depth. The term is retained because earlier RDT work used shell language, but no independent shell theory is claimed.

A **path** is the sequence of left/right branch decisions from the root to a cell. An **ancestor** of a cell is any cell on the path from the root to that cell. A **descendant** is any cell below a given cell.

A **stable label** is a bucket identifier assigned to an active cell. Stable labels are designed to change as little as possible under resize.

A **resize operation** changes the requested active bucket count from `k1` to `k2`. RDT-v1 does not rebuild the hierarchy from scratch. It replays the same split history to `k1` and `k2` active cells, then compares labels.

**Movement cost** is:

`movement = count(label_before != label_after) / n`.

**Locality cost** is within-label variance divided by global variance. Lower values mean points sharing a label are tighter relative to the whole dataset.

**Load imbalance** is:

`imbalance = max_bucket_count / mean_nonempty_bucket_count`.

The benchmark's combined score is:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

The weights are development weights, not universal constants. They express the current benchmark's emphasis and should be varied in future sensitivity analysis.

A **coverage schedule** is a deterministic recipe for generating numerical test inputs. RDT-cover uses boundaries, midpoints, powers of ten, corners, and shell-like jitter. An **edge-case class** is a predeclared input class that the test generator should discover.

## 5. Methods

### 5.1 RDT-v1 Hierarchy Construction

RDT-v1 builds a deterministic binary hierarchy:

1. Start with a root cell containing all point indices.
2. For each splittable active cell, compute coordinate spread by dimension.
3. Score each splittable cell as `cell_size * max_coordinate_spread`.
4. Select the active cell with highest score.
5. Split along the dimension with largest spread.
6. Use deterministic median partitioning along that dimension.
7. Store the split and repeat until the requested maximum leaf count, minimum cell size, or maximum depth stops construction.

The splitter is intentionally simple. The paper does not claim that this is an optimal tree. The purpose is to isolate the role of stable label inheritance.

### 5.2 Stable Ancestor-Label Inheritance

The stable label rule is:

1. The root starts with label `0`.
2. When an active cell with label `L` splits, the left child inherits `L`.
3. The right child receives the next unused label.
4. Labels for all other active cells remain unchanged.

For a partition with `k` active cells, RDT replays the first `k - 1` splits. For resize from `k1` to `k2`, labels are computed by replaying the same split history to each active count. Movement is measured by comparing point labels before and after resize.

This is the central mechanism in the paper. The remapped-label ablation keeps the recursive structure but discards inheritance. If remapped labels perform as well as stable labels, the main mechanism claim fails.

### 5.3 Stable Partition Baselines

The current stable partition benchmark compares RDT stable labels with:

- Jump Consistent Hash,
- rendezvous hashing,
- modulo hashing,
- Morton ordering,
- principal-axis sorting,
- grid partitioning,
- remapped-label RDT.

The baseline set is not complete. Hilbert, H3, S2, geohash, virtual-node hashing, memory scaling, and production workloads remain required before stronger claims.

### 5.4 RDT-Cover

RDT-cover creates numerical test inputs from a bounded domain. The schedule includes:

- domain center,
- min/max boundaries,
- zero if zero lies inside the domain,
- positive and negative powers of ten,
- recursive midpoints,
- corners,
- shell-like jitter around the center.

The hybrid mode, RDT+Sobol, inserts deterministic edge anchors first and fills the remaining budget with Sobol points.

### 5.5 Residual Sampler, Shell Drift, and Codec Boundary Tests

The repository includes three non-headline modules because they clarify the boundary of the framework.

The residual sampler ranks points using residual magnitude, a gradient proxy, shell/depth metadata, and coverage pressure. It is research-only because it lacks full downstream PDE/PINN training validation.

Shell drift compares depth/shell distributions over windows. It is diagnostic-only because simple histogram and mean/std baselines remain competitive.

Recursive delta preprocessing transforms byte sequences before standard compression. It is not an active package claim because it helps ramp-like synthetic bytes but not general real corpora.

## 6. Experiments

### 6.1 Stable Partitioning

The stable partition benchmark evaluates resize tasks:

- `16 -> 20`,
- `32 -> 40`,
- `64 -> 80`.

Synthetic datasets include uniform, clustered, diagonal, and hotspot-tail point clouds. The real-data benchmark uses California Housing coordinates from scikit-learn, with `n = 20,640`.

Metrics are movement, locality, load imbalance, assignment time, build time, and combined score.

### 6.2 Stable Label Ablation

The ablation compares:

- RDT with stable labels,
- RDT with remapped centroid labels,
- Jump Hash,
- Morton equal chunks.

This test answers whether stable label inheritance matters beyond the recursive split structure.

### 6.3 RDT-Cover

The RDT-cover benchmark uses a two-dimensional numerical domain and predeclared seeded edge-case classes:

- zero boundary,
- large cancellation,
- power transition,
- outer corner,
- thin annulus.

Compared methods are:

- RDT full,
- RDT+Sobol,
- powers-only,
- midpoints-only,
- boundaries-only,
- random uniform,
- Sobol,
- Latin hypercube.

The main metric is the number of edge-case classes found at fixed budget.

### 6.4 Geometry Validation

The geometry validation benchmark checks selected known forms:

- disk area,
- sphere volume,
- cone volume,
- cube volume,
- cylinder volume.

Radii tested are `0.5`, `1.0`, and `2.0`. The current baseline is a coarse midpoint schedule.

### 6.5 Residual Sampling

Residual sampling benchmarks include:

- synthetic sharp front,
- synthetic two hotspots,
- synthetic oscillatory field,
- real California Housing residual field.

Compared methods include top residual, top residual plus gradient, residual-proportional sampling, uniform sampling, RDT default, RDT tuned, RDT no coverage, and RDT no gradient.

These are point-selection metrics, not solver-training results.

### 6.6 Boundary Evidence: Drift and Codec

Drift experiments include synthetic shifts and the NAB ambient temperature time series. Codec experiments include synthetic ramp, random bytes, repeated text, Project Gutenberg Alice, California numeric CSV, and NAB CSV.

These experiments are not intended as flagship results. They document where broad RDT claims should not be made.

## 7. Results

### 7.1 Stable Partitioning on Real Coordinates

On California Housing coordinates, lower combined score is better.

| Resize | RDT stable | Jump Hash | Rendezvous Hash | Grid | Morton sort | Principal sort |
|---|---:|---:|---:|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.6585 | 1.9999 | 0.9195 | 0.8942 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.6710 | 2.4919 | 0.9674 | 0.9529 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.6819 | 4.0003 | 0.9830 | 0.9630 |

![California Housing resize score](../docs/figures/stable_partition_real.svg)

RDT wins the tested combined score because it preserves much more locality than hash methods while moving fewer points than spatial ordering methods. Grid is fast but performs poorly on load imbalance under these tested bucket counts.

### 7.2 Stable Label Ablation

Stable labels outperform remapped labels on representative real and synthetic tasks.

| Dataset | Resize | Stable labels | Remapped labels | Jump Hash |
|---|---:|---:|---:|---:|
| California Housing | 16 -> 20 | 0.4386 | 1.2198 | 0.6583 |
| California Housing | 64 -> 80 | 0.4641 | 1.2762 | 0.6790 |
| Synthetic uniform | 16 -> 20 | 0.2003 | 0.8439 | 0.6599 |
| Synthetic clustered | 16 -> 20 | 0.2639 | 0.9513 | 0.6601 |

![Stable label ablation](../docs/figures/stable_partition_ablation.svg)

This is the strongest mechanism evidence. It supports stable ancestor-label inheritance, not recursion alone.

### 7.3 RDT-Cover Edge-Case Discovery

At the tested budget:

| Method | Mean bug classes found | Mean total hits | Mean centered discrepancy |
|---|---:|---:|---:|
| RDT full | 5.00 | 75.20 | 0.11446 |
| RDT+Sobol | 5.00 | 70.20 | 0.02822 |
| Powers-only | 4.00 | 89.40 | 0.00108 |
| Midpoints-only | 3.00 | 63.00 | 0.00066 |
| Boundaries-only | 3.00 | 40.00 | 0.00046 |
| Random uniform | 2.00 | 35.60 | 0.00044 |
| Sobol | 2.00 | 34.20 | 0.00000 |
| Latin hypercube | 2.00 | 46.60 | 0.00002 |

![RDT-cover edge-case discovery](../docs/figures/coverage_ablation.svg)

Sobol has excellent discrepancy, but it misses seeded edge classes. RDT-cover spends budget on deterministic edge anchors and therefore finds more edge classes in this corpus. The hybrid keeps full discovery while improving fill quality relative to RDT-only.

### 7.4 Geometry Validation

| Radius | RDT max relative error | Midpoint baseline max relative error |
|---|---:|---:|
| 0.5 | 0.0003674 | 0.0004025 |
| 1.0 | 0.0003674 | 0.0004025 |
| 2.0 | 0.0003674 | 0.0004025 |

![Geometry validation error](../docs/figures/geometry_error.svg)

The current geometry result is small but clean: known formulas, declared error, and a simple baseline. It should not be generalized until stronger numerical integration baselines are added.

### 7.5 Residual Sampling

| Field | Winner | RDT tuned | Top residual |
|---|---|---:|---:|
| Synthetic sharp front | RDT tuned | 0.7241 | 0.6993 |
| Synthetic two hotspots | RDT tuned | 0.7762 | 0.6381 |
| Synthetic oscillatory | Top residual | 0.6280 | 0.8896 |
| Real California residual | Top residual | 0.2839 | 0.4596 |

![Residual sampler real-data failure](../docs/figures/residual_real.svg)

This mixed result is important. RDT residual sampling may help when separated regions and coverage pressure matter. It loses when directly selecting the largest residuals is better. No PDE/PINN training claim is supported.

### 7.6 Runtime Caveat

![Runtime caveat](../docs/figures/performance_50k_uniform.svg)

RDT is not currently the fastest raw assignment method. Timing is machine-local, but the qualitative lesson matters: the stable partition claim is a tradeoff claim, not a throughput claim.

### 7.7 Codec and Drift Boundary Evidence

Recursive delta preprocessing helps ramp-like synthetic data but loses on real text and CSV corpora:

| Corpus | Best method | RDT delta ratio | zlib ratio |
|---|---|---:|---:|
| Synthetic ramp | RDT delta | 321.2549 | 40.1569 |
| Project Gutenberg Alice | bz2 | 2.3085 | 2.8219 |
| Synthetic random | zlib | 0.9987 | 0.9993 |

Shell drift can detect some synthetic shifts, but simple baselines remain competitive. Both lines should stay outside headline claims.

## 8. Discussion

The evidence suggests a narrower interpretation of RDT than the early research program. RDT is not best understood as a universal algorithm. It is better understood as a way to attach recursive hierarchy metadata to data, then test whether that metadata preserves or exposes something useful.

Stable partitioning is the clearest case. The stable label rule creates a direct link between ancestry and movement. The ablation shows that the inheritance rule matters. This makes the result interpretable: the method works because the label history is not discarded during resize.

RDT-cover is also interpretable. It does not try to optimize discrepancy alone. It intentionally includes numerical stress regions. That makes it useful when failure classes are boundary- or scale-sensitive. The result is promising, but it must be tested against property-based testing and real bug corpora.

The failure cases are not incidental. They define the framework boundary. Residual sampling requires stronger downstream validation. Shell drift needs to beat simple baselines. Recursive delta preprocessing is narrow. Raw spatial index claims need speed and memory evidence.

The practical lesson is that future RDT work should use this sequence:

1. Define the recursive object.
2. Identify the property it should preserve or expose.
3. Choose strong non-RDT baselines.
4. Run an ablation that removes the RDT-specific mechanism.
5. Report failures and non-claims.

## 9. Limitations

The stable partition benchmark needs stronger baselines: Hilbert curves, H3, S2, geohash, virtual-node consistent hashing, memory scaling, and larger real workloads.

The combined score uses fixed development weights. Future work should report sensitivity over movement, locality, and load weights.

RDT-cover is tested on a seeded synthetic corpus. This is good mechanism evidence but not real software-failure evidence. Hypothesis, fuzzers, adaptive random testing, and numerical mutant corpora are needed.

The geometry validation benchmark uses selected known forms and a simple baseline. Equal-budget quadrature, Monte Carlo, quasi-Monte Carlo, and convergence curves are required before stronger numerical-method claims.

Residual sampling is not evaluated in full solver or training loops. Point-selection metrics cannot support PDE/PINN training claims.

The current implementation is a research implementation. Performance optimization, memory profiling, and API hardening remain needed before a stable library release.

## 10. Conclusion

RDT Adaptive Hierarchies distills a broad recursive-depth research line into a smaller, testable computational framework. The strongest current evidence supports stable ancestor-label inheritance for resize partitioning and deterministic RDT-cover for seeded numerical edge-case generation. The framework is useful when recursive metadata is tied to a measurable property and tested against baselines.

The paper should not be read as a universal RDT theory. It is a bounded methods report with reproducible code, clear baselines, ablations, and documented failures. The next publication-grade step is to strengthen the stable partition and RDT-cover baselines while preserving the current standard: no claim without a definition, metric, ablation, and failure condition.

## Data and Code Availability

Code, tests, examples, figures, and result artifacts are available in the accompanying repository. Raw artifacts are stored under `results/raw/`, interpreted summaries under `results/`, and reproducibility commands under `docs/reproducibility.md`.

## Acknowledgments

This work grew out of the author's earlier Recursive Division Tree experiments and the Zenodo RDT preprint [1]. The current package is a narrowed and benchmarked form of that research line.

## References

[1] Reid, S. (2025). *Recursive Division Tree: A Log-Log Algorithm for Integer Depth* (Version v2). Zenodo. https://doi.org/10.5281/zenodo.18012166

[2] Lamping, J., & Veach, E. (2014). *A Fast, Minimal Memory, Consistent Hash Algorithm*. arXiv:1406.2294. https://arxiv.org/abs/1406.2294

[3] Thaler, D. G., & Ravishankar, C. V. (1998). Using name-based mappings to increase hit rates. *IEEE/ACM Transactions on Networking*, 6(1), 1-14.

[4] H3 Project. *H3: A Hexagonal Hierarchical Geospatial Indexing System*. https://h3geo.org/docs/

[5] S2 Geometry. *S2 Cell Hierarchy*. https://s2geometry.io/devguide/s2cell_hierarchy

[6] SciPy Developers. *Quasi-Monte Carlo submodule: Sobol and Halton sequences*. https://docs.scipy.org/doc/scipy/reference/stats.qmc.html

[7] Hypothesis Developers. *Hypothesis: Property-Based Testing for Python*. https://hypothesis.readthedocs.io/

[8] Chen, T. Y., Kuo, F.-C., Merkel, R. G., & Tse, T. H. (2010). Adaptive random testing: The ART of test case diversity. *Journal of Systems and Software*, 83(1), 60-66.

[9] Wu, C., Zhu, M., Tan, Q., Kartha, Y., & Lu, L. (2022). *A comprehensive study of non-adaptive and residual-based adaptive sampling for physics-informed neural networks*. arXiv:2207.10289. https://arxiv.org/abs/2207.10289
