# NEXUS Decision Envelope

The NEXUS Decision Envelope is the v1.3.0 self-bootstrap surface.

It gathers current origin, Cortex memory state, predictive timing, predictive evolve, certificate resume, active wound state, algorithm cards, discovery cards, and git scope into one recommendation-only packet:

```text
origin -> memory -> runtime pressure -> wounds -> certificates -> git scope -> normalized recommendations -> selected next action
```

The envelope makes NEXUS feel self-bootstrapping because a new agent or chat can run one lane and see the current operational truth without loading the whole repository into context.

It does not execute the selected action. It does not grant authority. It does not skip final evolve.

## Outputs

- `reports/nexus_decision_envelope_latest.json`
- `state/decision/nexus_decision_envelope_latest.json`

## Command

```powershell
.\scripts\nexus.ps1 decision-envelope
```

## Boundary

Self-bootstrap means self-orientation, not self-authorization.

```text
recommendation != execution
self-observation != self-authority
final evolve remains required before commit
```
