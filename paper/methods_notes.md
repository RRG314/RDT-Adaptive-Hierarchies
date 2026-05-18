# Methods Notes

These notes are the bridge between the implementation and a future methods section. They should stay aligned with `src/rdt_adaptive_hierarchy`.

## RDT-v1 Reference Hierarchy

Input is a numeric array `X` with `n` points and `d` dimensions. The hierarchy starts with one root cell containing every point index.

At each split step:

1. Compute each active cell's coordinate spread by dimension.
2. Score each splittable active cell as `cell_size * max_spread`.
3. Choose the active cell with highest score.
4. Choose the split dimension with largest spread.
5. Partition the cell by the deterministic median order along that dimension.
6. Store parent id, child ids, depth, split dimension, and split threshold.

This rule is simple by design. It is not a learned partitioner, not a KDTree replacement, and not an optimized spatial index. It exists so the stable-label mechanism can be tested without hiding behavior behind a complex splitter.

## Stable Label Replay

For a requested bucket count `k`, replay the first `k - 1` stored splits. The active leaves become the current partition.

Stable-label rule:

- The root starts with label `0`.
- When a labeled active cell splits, the left child inherits the parent's label.
- The right child receives the next unused label.
- Labels for all other active cells remain unchanged.

This means resize from `k1` to `k2` does not assign labels from scratch. It extends the earlier partition by exposing additional branches of the same split history.

## Metrics

Movement:

`movement = count(label_before != label_after) / n`.

Locality:

The current implementation uses within-label variance divided by global variance. Lower locality cost means points sharing a label are tighter relative to the whole dataset.

Load imbalance:

`imbalance = max_bucket_count / mean_nonempty_bucket_count`.

Combined score:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

The weights are development weights. They reflect the current benchmark emphasis and should be reported honestly as such. A future paper should include score-weight sensitivity and task-specific objective choices.

## Baselines

Stable partition baselines currently include:

- Jump Consistent Hash,
- rendezvous hashing,
- modulo hashing,
- Morton ordering,
- principal-axis sorting,
- grid partitioning,
- remapped-label RDT ablation.

Implemented release-hardening, deep-validation, and submission-validation baselines:

- virtual-node consistent hashing,
- Hilbert ordering,
- H3,
- S2,
- geohash,
- shuffled-label null control with matched counts,
- random-label null control.

Remaining before submission:

- workload-specific production partitioners,
- larger real geospatial/vector/shard migration workloads,
- isolated per-method memory profiling,
- parameter sensitivity for virtual-node counts and geospatial levels.

## RDT-Cover Method

RDT-cover generates a deterministic set of numeric test cases from a bounded domain. The schedule includes:

- domain center,
- minimum and maximum boundaries,
- zero when it lies inside the domain,
- powers of ten, powers of two, and their negatives,
- recursive midpoints,
- corners,
- shell-like jitter around the center.

The benchmark also includes boundary-only, midpoint-only, powers-only, Sobol, Halton, Latin hypercube, random, hybrid RDT+Sobol, and Hypothesis-targeted baselines. The intended use is not to replace random or property-based testing. It is to ensure that known numerical stress regions appear under a finite budget when explicit properties are not yet formalized.

The expanded 14-class corpus narrowed the RDT-cover claim. At budget `2048`, Hypothesis-targeted coverage found `13/14` classes, powers-only found `11/14`, and full RDT-cover found `10/14`. A separate floating-point property benchmark found that RDT-cover caught several numerical traps but missed the tangent-periodicity failure at budget `512`. This means the paper should not imply that the full RDT schedule is the best edge-case schedule. The defensible point is that deterministic multiscale anchors beat blind random, Sobol, Halton, and Latin hypercube on this corpus and provide reproducible property-free coverage when explicit predicates are not yet available.

## Residual Sampler Method

The residual sampler ranks candidate points using:

- residual magnitude,
- a gradient proxy,
- shell/depth information,
- coverage pressure.

It is intentionally marked research-only. The existing metric measures candidate selection quality, not downstream solver or training quality. A publishable PDE/PINN claim would need full training loops, convergence metrics, RAR/RAD baselines, and conservation/stability checks where relevant.

The deep-validation run added `multi_front` and a real California Housing residual field. RDT variants won only selected synthetic cases. Greedy or stratified residual baselines won the real California, oscillatory, and multi-front cases. This belongs in the limitations section rather than the contribution list.

## Geometry Validation Method

The geometry validation module evaluates selected known forms:

- disk area,
- sphere volume,
- cone volume,
- cube volume,
- cylinder volume.

The deep-validation run also added simple integral checks for an interval polynomial, square product, smooth sine/cosine function, triangle indicator, and annulus indicator. Sobol/QMC beats RDT on several of those tasks. The current result is a bounded numerical validation. It should be described as a schedule comparison against simple baselines, not as evidence for a new geometry theory or a generally better integrator.

## Result Reporting Rules

Every result table should include:

- dataset or synthetic generator,
- seed range,
- resize pair or budget,
- method names,
- metric definitions,
- best method,
- limitations,
- raw artifact path.

Every public claim should include a failure condition. If stronger baselines close the gap, the claim should be narrowed or removed.
