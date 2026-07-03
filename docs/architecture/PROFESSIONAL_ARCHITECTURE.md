# NEXUS GATE Professional Architecture

NEXUS GATE is a governed transfer boundary between agent frameworks.

## Planes

```text
Adapter Plane
  raw framework events
  -> normalized StatePacket

Hot Route Plane
  schema
  codec
  registry snapshot
  capability bitset
  authority contract
  route decision

Cold Evidence Plane
  shadow reports
  retrospective scoring
  wounds
  demotion
  recalibration
  replay
  retirement

Ledger Plane
  append-only JSONL events
  compile reports
  route reports
  promotion reports
```

## Low-Latency Rule

The hot path must remain bounded.

Allowed hot-path work:

```text
decode
schema check
registry snapshot read
authority bitset check
mode decision
ledger stub
```

Cold-path work:

```text
deep scoring
shadow analysis
wound routing
replay
demotion
recalibration
registry maturity update
```

## Dual-Shell Runtime Rule

Runtime loops and promotion paths must exist in both PowerShell and Bash.

Both surfaces must invoke the same gated compiler before cycling or promoting.