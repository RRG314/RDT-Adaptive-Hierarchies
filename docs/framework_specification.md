# Framework Specification

## Data Domain

The data domain is a finite numeric array `X` with shape `(n_points, n_dimensions)`. Each row is a point. RDT-v1 does not assume that the points are geographic, physical, or random. It only assumes numeric coordinates that can be split by thresholds.

## Recursive Cell

A recursive cell is a node in a rooted tree. Each cell stores:

- a cell id,
- a parent id,
- a depth,
- the indices of points in the cell,
- an optional split dimension,
- an optional split threshold,
- optional left and right child ids.

The root cell contains all points. Child cells are created by splitting a parent cell.

## Hierarchy Construction

RDT-v1 uses a deterministic binary split rule:

1. Start with the root cell.
2. Score each splittable active cell by `cell_size * maximum_coordinate_spread`.
3. Split the highest-scoring cell.
4. Split along the coordinate dimension with the largest spread.
5. Split at the median partition of that coordinate.
6. Repeat until the requested maximum number of leaves, minimum cell size, or maximum depth stops construction.

This construction is intentionally simple. The goal is to test stable hierarchy behavior, not to hide performance inside a learned or tuned splitter.

## Depth And Shell Metadata

Depth is the number of edges from the root to a cell. In RDT-v1, shell is equal to depth. Future work may define richer shells, but current claims use only the depth-shell definition.

## Stable Labels

Stable labels are bucket ids assigned to active cells. When an active cell splits:

- the left child inherits the parent label,
- the right child receives the next unused label,
- all other active cell labels are unchanged.

This label rule is the main mechanism supported by current ablations.

## Resize Operation

A resize changes the number of active cells. The hierarchy does not rebuild from scratch. Instead, it replays the same split sequence up to the requested active cell count and applies stable labels.

For a resize from `k=16` to `k=20`, the first 15 splits define the old active cells and the first 19 splits define the new active cells. Movement is the fraction of points whose labels changed.

## Refinement Operation

Refinement selects active cells or candidate points using scores and a budget. RDT-v1 exposes score-based selection for active cells but does not mutate the fitted tree after construction. This keeps the reference behavior deterministic.

## Coverage Schedule

RDT-cover generates test points from:

- domain boundaries,
- zero when it lies inside the domain,
- powers of ten and their negatives,
- recursive midpoints,
- corners,
- shell-like jitter around the center.

RDT+Sobol combines those edge cases with Sobol fill. The hybrid is useful when both edge discovery and low-discrepancy fill matter.

## Metrics

Movement cost is the fraction of points whose label changes between two partitions.

Locality cost is within-cell variance divided by global variance. Lower is better.

Load imbalance is the maximum nonempty bucket count divided by the mean nonempty bucket count. A value of `1.0` is perfectly balanced.

Coverage discovery is the number of predeclared edge-case classes found by a generated set.

