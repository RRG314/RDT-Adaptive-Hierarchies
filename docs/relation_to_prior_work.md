# Relation To Prior Work

RDT Adaptive Hierarchies sits near several established areas. The current repo uses those areas to choose baselines and to keep claims bounded.

## Consistent Hashing

Consistent hashing addresses the problem of assigning keys to buckets while minimizing movement when buckets change. RDT stable partitioning shares the movement problem but adds spatial locality and load measurement. The current release includes Jump Hash, rendezvous hashing, and virtual-node consistent hashing baselines.

Jump Consistent Hash is a compact consistent hash method by Lamping and Veach. It is a primary movement baseline in this repo. See `REFERENCES.md`.

Rendezvous hashing, also called highest-random-weight hashing, is another standard assignment method. It is included as a baseline wrapper.

## Space-Filling Curves And Spatial Orderings

Morton/Z-order and Hilbert curves map multidimensional points into one-dimensional orderings that tend to preserve locality. Both are included as spatial-ordering baselines. Morton partitioning is faster than RDT in current timing checks and remains a necessary speed caveat.

## Geospatial Hierarchies

H3 and S2 are mature geospatial indexing systems. H3 partitions the world into hierarchical hexagonal cells. S2 uses a cell hierarchy on the sphere. RDT differs because it is data-adaptive rather than a fixed global grid, but that does not imply superiority. H3, S2, and geohash ordering baselines are now included; richer real geospatial workloads are still needed.

## Tree-Based Spatial Indexes

KDTree, quadtree, octree, R-tree, and BVH methods all use spatial hierarchy. RDT-v1 is not currently promoted as a raw range-query or nearest-neighbor index. Prior RDT spatial index wrappers matched exactness but did not establish speed gains.

The practical spatial-index branch of this research line lives in the companion repository [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index). That repository is the right place to evaluate `RDTIndex`, `RDTFastIndex`, optimized backends, range-query behavior, and kNN-oriented workloads. This repository cites it for provenance and comparison context, but keeps its own public claim focused on stable resize partitioning rather than replacing KDTree, grid, R-tree, H3, S2, or other mature spatial-index systems.

## Adaptive Mesh Refinement

Adaptive mesh refinement refines numerical grids where more resolution is needed. RDT residual sampling is related in spirit but does not yet have full PDE/PINN training evidence. It remains research-only.

## Quasi-Monte Carlo And Coverage

Sobol and Halton sequences are low-discrepancy sampling methods used in quasi-Monte Carlo. RDT-cover is different because it intentionally includes boundaries, powers, and midpoints. The hybrid RDT+Sobol mode combines edge anchors with low-discrepancy fill.

## Property-Based Testing And Adaptive Random Testing

Hypothesis and similar tools generate test cases from user-defined strategies. Adaptive random testing tries to spread test cases to improve failure discovery. The current release includes a Hypothesis-targeted coverage baseline that outperforms RDT-cover on the expanded seeded corpus when predicates are known. Current evidence is still limited to synthetic seeded numerical classes.

## Residual Adaptive Refinement

RAR, RAD, and RAR-D are important baselines for residual-based sampling in physics-informed neural networks. RDT residual sampling must beat or explain a failure mode of these methods before it can become more than a research module.

## Wavelets, Multiresolution, And Multiscale Entropy

RDT uses depth and shell metadata, but this repo does not claim a wavelet basis, a multiresolution transform, or a general entropy theory. Those areas are useful for comparison, not claims.
