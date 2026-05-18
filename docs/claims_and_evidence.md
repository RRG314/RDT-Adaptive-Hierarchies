# Claims And Evidence

This project keeps claims only when they have definitions, benchmark evidence, baseline comparison, and a failure condition.

## Stable Partition Claim

Claim: stable ancestor-label inheritance improves the movement/locality/load tradeoff in the tested resize tasks.

Evidence: in the 5-seed benchmark, RDT stable labels had the best combined score on clustered, diagonal, hotspot-tail, and uniform synthetic datasets. On California Housing coordinates, RDT stable labels had the best combined score for 16->20, 32->40, and 64->80 resize tasks. The release-hardening run adds Hilbert, H3, S2, geohash, and virtual-node consistent hashing; RDT stable labels remain best on the tested synthetic datasets.

Ablation: stable labels beat remapped labels on every tested partition task. California 16->20 scored `0.4386` for stable labels, `1.2198` for remapped labels, and `0.6583` for Jump Hash.

Failure condition: the claim weakens if stable labels do not beat remapped labels or if stronger baselines match the movement/locality/load tradeoff.

Allowed wording: RDT stable labels improve the tested resize tradeoff.

Forbidden wording: RDT is generally better than consistent hashing, H3, S2, KDTree, or spatial indexes.

## RDT-Cover Claim

Claim: RDT-cover improves seeded numerical edge-case discovery in the current test corpus.

Evidence: RDT full, RDT+Sobol, and Hypothesis-targeted coverage found all 5 seeded bug classes. Random, Sobol, and Latin hypercube found fewer in the release-hardening run.

Ablation: powers-only found 4 classes; midpoint-only and boundary-only found 3. The full schedule matters.

Failure condition: the claim weakens if adaptive random testing or a real numerical bug corpus finds the same failures faster at equal budget. The Hypothesis-targeted baseline already matches bug-class discovery on the seeded corpus when the predicates are known.

Allowed wording: RDT-cover is useful as a deterministic complement to random and low-discrepancy sampling when explicit properties are not yet available.

Forbidden wording: RDT-cover is generally better than property-based testing or fuzzing.

## Residual Sampler Claim

Claim: RDT residual sampling is a research candidate, not a supported general method.

Evidence: tuned RDT wins on synthetic sharp-front and two-hotspot fields, but top residual wins on the oscillatory field and real California residuals.

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

Evidence: local known-form validation reports mean max relative error `0.00036741` for the RDT schedule and `0.00040250` for the coarse midpoint baseline. Earlier benchmark-hub adapter evidence reported candidate `0.00036741236618786894` against baseline mean `0.004643523475071463`.

Failure condition: the claim weakens if equal-budget quadrature, Monte Carlo, or QMC dominates, or if convergence fails on additional known forms.

Allowed wording: the geometry helper is a bounded numerical validation object.

Forbidden wording: RDT proves a new geometry theory.
