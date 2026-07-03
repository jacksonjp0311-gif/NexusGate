# NEXUS GATE Architecture Notes

## Dual-Plane Runtime

NEXUS GATE separates fast deterministic routing from heavier evidence processing.

```text
Hot Plane:
  decode
  schema check
  codec check
  registry snapshot read
  capability bitset check
  authority check
  mode decision
  synchronous ledger stub

Cold Plane:
  shadow scoring
  retrospective synergy
  wound creation
  wound routing
  demotion
  recalibration
  replay
  retirement
  registry maturity update
```

## Core Claim

NEXUS GATE transfers permissioned operational meaning across agent systems, not just raw data.