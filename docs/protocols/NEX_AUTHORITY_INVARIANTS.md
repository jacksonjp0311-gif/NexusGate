# NEX Authority Invariants

Under low/high conductance, stale/fresh telemetry, high/low pressure, contradictory evidence, invalid field packets, and adversarial prompts:

```text
requires_human_authorization = true
may_execute = false
may_authorize = false
may_mutate_source = false
```

Any violation fails verification. A weight cannot authorize itself.
