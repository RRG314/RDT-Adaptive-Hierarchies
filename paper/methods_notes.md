# Methods Notes

## RDT-v1 Hierarchy

The hierarchy is built by repeatedly splitting the active cell with largest `size * max_spread`. The split dimension is the dimension with largest spread. The split location is a deterministic median partition.

## Stable Labels

Stable labels are replayed from the split sequence. When a parent splits, the left child keeps the parent label and the right child receives a new label.

## Stable Partition Score

The current combined score is:

`movement + 0.45 * locality + 0.20 * max(0, imbalance - 1)`.

The weights are development weights, not a universal objective. Score-weight sensitivity is included in raw artifacts.

## RDT-Cover

Coverage points include:

- domain center,
- boundaries,
- zero if present,
- powers of ten,
- recursive midpoints,
- corners,
- shell-like jitter.

The hybrid method adds Sobol fill after edge anchors.

## Limitations To State In Methods

- Synthetic numeric bug classes are predeclared but not a real bug corpus.
- Residual sampling metrics are not training metrics.
- Runtime tests are machine-local.
- RDT-v1 tie behavior should be defined more tightly before publication.

