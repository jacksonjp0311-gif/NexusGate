# NEXUS Toolbelt Console (v0.9.6–v0.9.7)

## Purpose

The **NEXUS Toolbelt Console** is a **read-only operator cockpit** that routes a human (or an AI assistant acting in recommendation mode) to the next correct local loop.

It is *not* an agent authority layer.

It exists to keep workflow evolution grounded in:

- compiler/test evidence
- wound-indexed resume (when failures exist)
- loop registry contracts (no arbitrary commands)

## Boundary (Non‑Authority)

The Toolbelt Console **does not**:

- execute arbitrary shell commands
- enable autonomous authority
- enable network access
- access secrets
- stage/commit/push git

It emits **packets and recommended commands only**.

## Canonical surfaces

### PowerShell

```powershell
.\scripts\nexus.ps1 toolbelt -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-dashboard -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-json -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-next -Tag "<intent>"
```

### Bash

```bash
bash scripts/nexus.sh toolbelt "<intent>"
bash scripts/nexus.sh toolbelt-json "<intent>"
bash scripts/nexus.sh toolbelt-next "<intent>"
```

### Python (direct)

```bash
python -m nexus_gate.loops.toolbelt --root . --intent "<intent>"
python -m nexus_gate.loops.toolbelt --root . --intent "<intent>" --json
```

## Output

The Toolbelt Console emits:

- a human-readable cockpit (`reports/nexus_toolbelt_cockpit_latest.txt`)
- a machine-readable packet (`state/loops/nexus_toolbelt_latest.json`)

The packet includes:

- repo HEAD + dirty status
- compiler status + failed gates (if any)
- recommended next loop
- recommended next command surface

## Relationship to Loop Cards

Toolbelt Console uses loop cards at:

- `state/loops/nexus_loop_cards_latest.json`

These cards are the HUD-ready mirror of the loop registry and remain **authority-bounded**.

## Claim boundary

This document is an operator orientation surface. It does not prove correctness, safety, or security.
