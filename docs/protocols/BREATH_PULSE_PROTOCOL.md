# Breath Pulse Protocol

NEXUS Breath is a read-only vital-sign surface for fast rehydration.

It summarizes:

- evidence freshness;
- runtime pressure;
- current Git scope;
- missing or stale surfaces;
- inhale / hold / exhale phase;
- one recommended next command.

Breath does not execute commands, authorize actions, prove correctness, replace
`evolve`, promote memory, or calibrate routes.

The rhythm is intentionally simple:

```text
inhale -> read identity and evidence
hold   -> stabilize pressure
exhale -> run a bounded recommendation gate
```

The packet is written to:

- `reports/nexus_breath_pulse_latest.json`
- `state/breath/nexus_breath_pulse_latest.json`

The breath packet may guide attention. It may not grant authority.
