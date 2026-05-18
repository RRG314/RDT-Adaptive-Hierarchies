# Known Limitations

RDT is not the fastest raw partitioner in current tests. In the 50k synthetic uniform timing check, grid and Morton were faster than RDT stable partitioning. RDT's current value is the movement/locality/load tradeoff, not raw speed.

The stable partition benchmark now includes Hilbert, H3, S2, geohash, and virtual-node consistent hashing. It still needs richer real geospatial workloads, production-style tuning, memory RSS profiling, and larger scaling tests.

RDT-cover is tested on a seeded numerical edge-case corpus. That is useful for mechanism testing, but it can favor the cases the schedule was designed to hit. A real Hypothesis-targeted baseline is now included and also finds all five seeded classes. Real bug corpora and property-agnostic comparisons remain needed before stronger claims.

The residual sampler is not validated as a PDE or PINN training method. Current evidence is mixed even before full training loops are added.

Shell drift does not beat simple baselines yet. It should be treated as a diagnostic view, not a detector.

The recursive delta codec is not an active public package module. It is preserved as evidence of a narrow transform idea because it helps ramp-like bytes, but real text and CSV corpora favor standard compressors.

The raw RDT spatial index is not promoted. Prior adapter evidence showed exactness, not speed superiority.
