# Outcome-Aware Arbiter Protocol

The v2.2 protocol records whether selected recommendations helped.

```text
Decision Envelope
-> selected action
-> human/gate outcome
-> recommendation outcome ledger
-> arbiter calibration
-> pressure memory
-> next Decision Envelope
```

## Surfaces

- `ledger/recommendation_outcomes.jsonl`
- `reports/nexus_recommendation_outcome_latest.json`
- `state/coherence/arbiter_calibration_latest.json`
- `state/coherence/pressure_memory_latest.json`

## Boundary

```text
outcome memory may calibrate routing
outcome memory may not self-authorize
outcome memory may not skip final evolve
```
