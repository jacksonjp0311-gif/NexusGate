# Causal Loop Hardening Protocol

Every causal route should carry:

- `repository_snapshot.epoch_id`
- `repository_snapshot.repository_commit`
- `repository_snapshot.source_status_hash`
- `repository_snapshot.input_snapshot_hash`
- typed `coherence.state`
- normalized wound activity
- clamped confidence
- deterministic arbiter selection
- source packet freshness metadata when available

## Control Law

```text
S_n + evidence_n -> recommendation_n+1
```

No recommendation may become execution without human authorization and final gates.
