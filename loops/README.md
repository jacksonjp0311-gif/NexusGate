# Nexus Meta Loops

## RCC Nexus Echo Location

Sphere Position:

- Shell: outer
- Meridian(s): runtime, rehydration, loops, evidence
- Sector: loops
- Version / TTL: NG-META-LOOP-v0.9.0 / 180 days

Local Role:

- Root-level human and AI visible loop registry surface.
- Declares local named loops that generated scripts can trigger instead of duplicating full operational logic.

## Rule

```text
Generated scripts should trigger local loops by name.
The repository owns the loop body.
The script owns only the current intent and minimal patch.
```

## Canonical Trigger

```powershell
python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "inspect repo" --json
python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "patch bounded surface" --json
python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "verify bounded surface" --execute --human-authorized --json
```

## Claim Boundary

Nexus meta-loops are local orchestration receipts. They do not prove correctness, safety, security, production readiness, memory truth, autonomous authority, rollback, or permission to commit/push without explicit human authorization.