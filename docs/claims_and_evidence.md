# Claims And Evidence

This project keeps claims only when they have definitions, benchmark evidence, baseline comparison, and a failure condition.

## Stable Partition Claim

Claim: stable ancestor-label inheritance improves the movement/locality/load tradeoff in the tested resize tasks.

Evidence: in the deep-validation benchmark, RDT stable labels had the best combined score in `40` of `40` tested dataset/resize tasks. The run covered uniform, clustered, diagonal, hotspot-tail, anisotropic Gaussian, ring/annulus, two-cluster imbalance, and California Housing coordinate datasets; resize pairs `8->10`, `16->20`, `32->40`, `64->80`, and `128->160`; and hash, virtual-node hash, geospatial, spatial-order, grid, remapped-label, shuffled-label, and random-label baselines.

Ablation: stable labels beat remapped labels on every tested partition task. In the deep-validation summary, California Housing `16->20` scored `0.4686` for stable labels, `1.2806` for remapped labels, and `0.6746` for Jump Hash. Across all rows, the mean combined score was `0.2905` for stable labels, `0.8620` for remapped labels, `1.0806` for shuffled labels with matched counts, and `1.0625` for random labels.

Failure condition: the claim weakens if stable labels do not beat remapped labels or if stronger baselines match the movement/locality/load tradeoff.

Allowed wording: RDT stable labels improve the tested resize tradeoff.

Forbidden wording: RDT is generally better than consistent hashing, H3, S2, KDTree, or spatial indexes.

## RDT-Cover Claim

Claim: RDT-cover is a deterministic multiscale edge-case generator that improves over blind random, low-discrepancy, and Latin hypercube sampling on the current seeded corpus, but it is not the strongest method in the expanded benchmark.

Evidence: the expanded deep-validation corpus has `14` seeded edge-case classes. At budget `1024`, Hypothesis-targeted coverage found `13` classes, the powers-only ablation found `11`, full RDT-cover found `10`, boundary-only found `9`, RDT+Sobol found `9`, and random, Sobol, Halton, and Latin hypercube each found `4`.

Ablation: the powers-only ablation outperformed full RDT-cover on class count in this expanded corpus. This weakens the older claim that the full schedule is the clearly best deterministic construction. The useful mechanism is better described as deterministic inclusion of scale and boundary anchors, with RDT ordering providing a reproducible way to combine those anchors with shell/midpoint coverage.

Failure condition: the claim weakens further if adaptive random testing, Hypothesis, or a real numerical bug corpus finds the same failures faster at equal budget, or if RDT-cover adds no classes beyond simpler boundary/power schedules.

Allowed wording: RDT-cover is useful as a deterministic complement to random and low-discrepancy sampling when explicit properties are not yet available.

Forbidden wording: RDT-cover is generally better than property-based testing or fuzzing.

## Residual Sampler Claim

Claim: RDT residual sampling is a research candidate, not a supported general method.

Evidence: tuned RDT wins on the two-hotspot field and remains competitive on sharp-front fields, but top residual, top residual gradient, or grid-stratified residual baselines win on California residuals, multi-front, and oscillatory fields.

Failure condition: if RDT does not beat RAR/RAD or greedy residual methods on full PDE/PINN training error, it should remain research-only.

Allowed wording: RDT residual sampling is mixed and experimental.

Forbidden wording: RDT improves PDE or PINN training generally.

## Shell Drift Claim

Claim: shell drift is diagnostic-only.

Evidence: shell drift can detect some synthetic shifts, but simple baselines such as histogram divergence and mean/std are competitive or better. The real NAB pass did not support a strong anomaly detection claim.

Failure condition: if shell drift does not beat simple baselines on delay and false positives, it remains auxiliary diagnostics.

Allowed wording: shell drift can be inspected as a scale-sensitive diagnostic.

Forbidden wording: shell drift is a superior anomaly detector.

## Delta Codec Claim

Claim: recursive delta preprocessing is a narrow observation for ramp-like structured bytes.

Evidence: RDT delta strongly improves a synthetic ramp corpus. Standard compressors win on Project Gutenberg Alice and real CSV corpora.

Failure condition: if roundtrip fails, header cost is ignored, or standard compressors win on target corpora, no compression superiority claim is allowed.

Allowed wording: recursive delta preprocessing can help ramp-like data.

Forbidden wording: RDT is a general compressor.

## Geometry Validation Claim

Claim: recursive-depth geometry validation reproduces selected known forms within declared tolerance.

Evidence: local known-form validation reports mean max relative error `0.00036741` for the RDT schedule and `0.00040250` for the coarse midpoint baseline. The added simple-integral checks narrow the claim: Sobol/QMC beats RDT on annulus, smooth, triangle, and interval examples, while coarse midpoint ties or wins on the unit-square product example.

Failure condition: the claim weakens if equal-budget quadrature, Monte Carlo, or QMC dominates, or if convergence fails on additional known forms.

Allowed wording: the geometry helper is a bounded numerical validation object.

Forbidden wording: RDT proves a new geometry theory.

## Spatial Index Boundary

Claim status: companion-repo context only.

Evidence: the separate [RDT Spatial Index](https://github.com/RRG314/rdt-spatial-index) repository contains the range-query and kNN-oriented implementation line. Earlier adapter evidence showed exactness for RDT index wrappers under controlled synthetic checks, but did not establish general speed superiority over mature spatial-index families.

Allowed wording: RDT spatial indexing is a related implementation branch and should be evaluated in its own repository against KDTree, grid, R-tree/BVH, H3/S2/geohash, and workload-specific baselines.

Forbidden wording: RDT Adaptive Hierarchies replaces standard spatial indexes.
