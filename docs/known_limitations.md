# Known Limitations

RDT is not the fastest raw partitioner in current tests. In the 50k synthetic uniform timing check, grid and Morton were faster than RDT stable partitioning. RDT's current value is the movement/locality/load tradeoff, not raw speed.

The stable partition benchmark now includes Hilbert, H3, S2, geohash, virtual-node consistent hashing, and targeted rendezvous hashing. The submission-validation run strengthened the movement/locality/load claim across 12 workloads, five resize pairs, and 10 seeds. It now includes public US cities, California Housing coordinates, sklearn digits, sklearn breast-cancer features, RSS memory snapshots, and automated stress tests for duplicate points, all-same degeneracy, high-dimensional inputs, and adversarial ordering. It still needs larger production-style shard migration workloads, task-specific tuning, isolated per-method memory profiling, and broader real geospatial/vector datasets.

RDT-cover is tested on a seeded numerical edge-case corpus and a separate floating-point property benchmark. Those are useful for mechanism testing, but they can still favor known numerical traps. The submission-validation corpus kept the claim narrow: Hypothesis-targeted coverage found `13/14` classes at budget `2048`, the powers-only ablation found `11/14`, and full RDT-cover found `10/14`. In the property benchmark, RDT-cover missed the tangent-periodicity failure at budget `512`. Real bug corpora, adaptive random testing, and property-agnostic comparisons remain needed before stronger claims.

The residual sampler is not validated as a PDE or PINN training method. Current evidence is mixed even before full training loops are added: RDT variants help on selected synthetic sharp-front and hotspot fields, but lose on oscillatory, multi-front, and real California residual fields.

The geometry validation module is bounded. It passes selected known-form checks, but Sobol/QMC beats RDT on several simple integration tasks. It should not be described as a new geometry theory or a generally superior integration method.

Shell drift does not beat simple baselines yet. It should be treated as a diagnostic view, not a detector.

The recursive delta codec is not an active public package module. It is preserved as evidence of a narrow transform idea because it helps ramp-like bytes, but real text and CSV corpora favor standard compressors.

Raw RDT spatial indexing is handled in the companion [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index) repository. This package cites that work for provenance and comparison context, but does not claim to replace KDTree, grid, R-tree, H3, S2, or other mature spatial-index systems.
