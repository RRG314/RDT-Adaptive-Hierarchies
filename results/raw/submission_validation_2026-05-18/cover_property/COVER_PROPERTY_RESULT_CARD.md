# RDT-Cover Property Benchmark

This is not the seeded edge-class corpus. It evaluates ordinary floating-point properties and includes a targeted Hypothesis `find` baseline.

| Property | Best found-rate method | RDT found rate | Powers-only found rate | Hypothesis found rate |
|---|---|---:|---:|---:|
| division_roundtrip | `powers_only` | 1.00 | 1.00 | 1.00 |
| exp_log_roundtrip | `latin_hypercube` | 1.00 | 1.00 | 1.00 |
| sqrt_square_overflow | `halton` | 1.00 | 1.00 | 1.00 |
| symmetric_matrix_singularity | `powers_only` | 1.00 | 1.00 | 1.00 |
| tan_periodicity | `boundary_only` | 0.00 | 0.10 | 0.00 |
