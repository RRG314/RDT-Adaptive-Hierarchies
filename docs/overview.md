# Overview

RDT began as a broad recursive-depth idea explored across notebooks, experiments, and prototype repos. Those early experiments tested random number generation, geometry, spatial indexing, compression, physics diagnostics, retrieval, weather features, and more. The broadest claims did not survive benchmarking. The useful part that remains is smaller and easier to test.

This repo focuses on **RDT Adaptive Hierarchies**: deterministic recursive hierarchies with stable labels, ancestor paths, depth metadata, and coverage schedules. The framework is useful only when that hierarchy preserves or targets something measurable.

## The Core Story

The strongest finding is not that "recursion is powerful." The stronger and more precise finding is:

> Stable ancestor-label inheritance can reduce label movement during partition resize while retaining more locality than hash-only baselines.

That is the reason `rdt-stable-partition` is the lead application.

The second useful finding is:

> Deterministic recursive coverage can place finite-budget test cases at numerical boundaries, midpoints, powers, corners, and scale transitions that random or low-discrepancy samples can miss.

That is the reason `rdt-cover` is the second supported application.

Everything else is intentionally narrower:

- residual sampling is research-only,
- shell drift is diagnostic-only,
- recursive-depth geometry validation is a bounded known-form check,
- recursive delta preprocessing is not an active public module,
- broad entropy, crypto, physics, biology, retrieval, and compression claims are outside this package.

## What A New Reader Should Understand First

Imagine a set of points partitioned into 16 buckets. Later, the system needs 20 buckets. A naive relabeling can move many points. A hash method can minimize movement, but it does not know whether nearby points stay together. A spatial sort can group nearby points, but bucket boundaries may shift and move many points.

RDT builds a split history. When the number of active buckets grows, it replays more of that split history. The important rule is that when a bucket splits, one child keeps the parent label. Only the new child receives a new label.

![Stable label inheritance mechanism](figures/rdt_stable_label_mechanism.svg)

That is the mechanism tested by the stable-label ablation.

## Evidence Snapshot

The current evidence is strongest for stable partitioning.

On California Housing coordinates:

| Resize | RDT stable | Jump Hash | Morton sort |
|---|---:|---:|---:|
| 16 -> 20 | 0.4386 | 0.6583 | 0.9195 |
| 32 -> 40 | 0.4945 | 0.6664 | 0.9674 |
| 64 -> 80 | 0.4641 | 0.6790 | 0.9830 |

The current evidence is also promising for RDT-cover:

| Method | Mean seeded edge-case classes found |
|---|---:|
| RDT full | 5.00 |
| RDT+Sobol | 5.00 |
| Random uniform | 2.00 |
| Sobol | 2.00 |

These are real benchmark numbers, not goals. They are also bounded numbers: stronger baselines and additional datasets are still needed.

## Why Some Ideas Are Not Promoted

The repo includes failure and limitation evidence because that is part of making the project credible.

Residual sampling loses to greedy top-residual selection on a real California Housing residual field. Shell drift does not consistently beat simple baselines. Recursive delta preprocessing helps ramp-like data but not general text or CSV compression. Raw RDT spatial indexes did not establish speed superiority.

Those results do not make RDT useless. They make the useful claim sharper: RDT is currently best treated as a stable recursive partition and deterministic coverage framework, not a universal algorithm.

## Recommended Reading Order

1. `README.md` for the public overview and headline numbers.
2. `docs/framework_specification.md` for formal objects and operations.
3. `results/README.md` for the evidence snapshot and interpretation.
4. `docs/claims_and_evidence.md` for allowed claim wording and failure conditions.
5. `docs/reproducibility.md` for commands and datasets.
6. `paper/outline.md` for the methods-paper plan.
