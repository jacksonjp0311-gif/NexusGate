# Causal Coherence Routing Protocol

The v2.1 routing protocol turns field state into recommendation pressure.

```text
Intent
-> Evidence Packets
-> Candidate Recommendations
-> Coherence Field
-> Recommendation Arbiter
-> Selected Action
-> Human Authorization
-> Gate / Receipt / Wound
```

## Required Packet Fields

Each recommendation should expose:

- `source`
- `action`
- `command`
- `why`
- `severity`
- `confidence`
- `estimated_cost`
- `blocking_conditions`
- `source_packet_hash`

## Arbiter Factors

- severity weight
- source priority
- confidence weight
- cost penalty
- blocking penalty
- stale evidence penalty
- coherence adjustment
- final evolve guard

## Law

```text
The route may adapt under pressure.
The route may not abandon evidence, gates, or human authority.
```
