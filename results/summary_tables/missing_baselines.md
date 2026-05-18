# Missing Or Blocked Baselines

Current practical baseline status:

| Area | Status |
|---|---|
| Jump Consistent Hash | included |
| Rendezvous hashing | included |
| Modulo hash | included |
| Virtual-node consistent hashing | included |
| Morton/Z-order | included |
| Hilbert ordering | included |
| Grid partition | included |
| Principal-direction sort | included |
| H3 | included through optional dependency `h3` |
| S2 | included through optional dependency `s2sphere` |
| Geohash | included through optional dependency `pygeohash` |
| Random uniform cover | included |
| Sobol cover | included |
| Halton cover | included |
| Latin hypercube cover | included |
| Hypothesis strategy | included |
| Adaptive random testing | not included; needed for stronger RDT-cover comparison |
| Real numerical bug corpus | not included; needed before stronger RDT-cover claims |
| RAR/RAD/PINN residual baselines | not included; residual sampler remains research-only |
| Full RSS/memory profiler | not included; current memory is `tracemalloc` only |
