# Chat Operation Contract

Version: v0.1.0

This contract binds the operator, the Electron/TUI surfaces, and the reflective intelligence layer.

## Hard rules

```text
No rehydration without failure/update visibility.
No compile pass, no promotion.
Chat output is recommendation-only.
Human authorizes durable mutation.
```

## Execution boundary

Chat may:
- read allowlisted surfaces
- run allowlisted lanes
- run HANDOFF scripts only with explicit operator authorization

Chat may not:
- mutate repo state autonomously
- run arbitrary shell commands

## Validation surface

- `python -m nexus_gate.compiler --root . --json`

## Claim boundary

This contract is a governance aid, not a proof.
