# Benchmark Interpretation

Benchmarks in this repo are meant to answer narrow questions. They do not prove a broad RDT theory.

## Stable Partition

Question: can stable ancestor-label inheritance reduce movement while preserving locality?

Current answer: yes, in the tested resize tasks. RDT stable labels beat remapped labels, Jump Hash, and Morton on the combined movement/locality/load score in the current synthetic and California Housing tests.

What it does not support: RDT is not the fastest raw method. Grid and Morton are faster in timing checks. The result supports a tradeoff, not general speed dominance.

Missing work: Hilbert, H3, S2, geohash, virtual-node hashing, memory scaling, and larger real workloads.

## RDT-Cover

Question: can deterministic boundary, midpoint, power, and shell coverage find seeded numerical edge cases?

Current answer: yes, in the current seeded corpus. RDT full and RDT+Sobol found all 5 classes. Random, Sobol, and Latin hypercube found 2.

What it does not support: RDT-cover is not yet shown to beat Hypothesis, fuzzers, or adaptive random testing on real software bugs.

Missing work: Hypothesis integration, real mutant corpora, time-to-first-failure, and shrinking/minimization.

## Residual Sampler

Question: can RDT coverage improve residual point selection?

Current answer: mixed. Tuned RDT helps synthetic sharp-front and two-hotspot fields. Top residual wins on oscillatory and real California residuals.

What it does not support: no broad PDE/PINN training claim is supported.

Missing work: full training loops, RAR/RAD/RAR-D baselines, convergence curves.

## Geometry Validation

Question: does recursive-depth refinement reproduce selected known forms?

Current answer: yes, for the included disk/sphere/cone/cube/cylinder checks. This is a bounded numerical validation result.

What it does not support: it does not prove a new geometry theory.

Missing work: equal-budget quadrature, Monte Carlo, QMC, more shapes, and convergence curves.

## Codec And Drift

Codec and drift results are preserved because they show boundaries of the idea. Shell drift is not a strong detector. Recursive delta preprocessing is useful only on ramp-like synthetic bytes. These should not be public headline modules.

