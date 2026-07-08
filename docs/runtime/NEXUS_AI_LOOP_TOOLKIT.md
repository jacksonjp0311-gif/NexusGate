
# NEXUS AI Loop Toolkit

v0.9.3 expands NexusGate into an AI-callable local loop toolkit.

The AI may recommend a named loop. NexusGate runs that loop locally through the registry and emits JSON evidence. The loop output can guide the next patch, wound closure, validation, or release brief. The AI does not gain autonomous authority.

## Toolkit Loops

| Loop | Function |
|---|---|
| `repo-radar` | Compact situational awareness before choosing an action. |
| `scope-hygiene` | Classify intended files versus runtime/report/backup residue. |
| `claim-boundary-audit` | Review docs for overclaim, proof, safety, or authority drift. |
| `surface-map` | Map repo organs, docs, tests, state, reports, and HUD surfaces. |
| `stale-surface-scan` | Find likely stale current-state/version references. |
| `next-action-router` | Recommend the next local loop from evidence. |
| `handoff-pack` | Build a compact ChatGPT/Codex handoff packet. |
| `dependency-preflight` | Separate environment wounds from code wounds. |
| `alignment-score` | Compute a transparent local alignment score. |
| `boundary-scan` | Verify loops and commands preserve non-authority boundaries. |
| `release-brief` | Produce a release summary before seal. |
| `evolution-radar` | Generate bounded next-evolution candidates. |

## Call Pattern

```powershell
python -m nexus_gate.loops.runner --root . --loop repo-radar --intent "what changed?" --execute --human-authorized --json
python -m nexus_gate.loops.runner --root . --loop scope-hygiene --intent "prepare stage" --execute --human-authorized --json
python -m nexus_gate.loops.runner --root . --loop next-action-router --intent "choose next loop" --execute --human-authorized --json
python -m nexus_gate.loops.runner --root . --loop evolution-radar --intent "what should evolve next?" --execute --human-authorized --json
```

## Boundary

These loops are local evidence tools. They do not grant autonomous authority, shell authority, git write authority, network access, secret access, memory promotion, safety proof, security proof, correctness proof, or commit/push permission.
