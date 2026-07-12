# Causal Loop Hardening Design

NEXUS v2.4 hardens the causal routing loop before adding more subsystems.

The route is now:

```text
repository snapshot
-> evidence packet freshness
-> typed coherence state
-> normalized wound state
-> clamped recommendation scoring
-> deterministic selected route
-> human authorization boundary
```

## Why These Wounds Were Missed

The v2.1 routing tests proved the happy path: low-but-nonzero coherence, one active repair recommendation, and normal confidence ranges. They did not include pathological control values:

- coherence score `0`
- inactive wound sentinels such as `none` or `clear`
- confidence values outside `[0, 1]`
- equal arbiter scores
- mixed-epoch packet inputs

The gap was not architectural blindness; it was missing adversarial control-state tests. v2.4 adds those tests and shared primitives so the same edge cases do not reappear in each organ.

## Boundary

Hardening may change recommendation pressure. It may not execute recommendations, skip final evolve, self-authorize, or claim proof from local evidence.
