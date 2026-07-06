# NexusCell Context Bridge

Version: v0.8.5

## Purpose

The NexusCell Context Bridge converts a read-only planner decision into a bounded evidence-reference packet.

It exists so local models and future execution-governance layers receive a compact context bridge instead of a whole-repository dump.

## Flow

```text
intent
-> NexusCell planner
-> capability vector
-> risk score
-> authority decision
-> context refs
-> evidence digests
-> context bridge hash
```

## Command

```powershell
python -m nexus_gate.nexus_cell.context_bridge --root . --intent "inspect docs only" --json
.\scripts\nexus.ps1 cell-context -Tag "inspect docs only"
```

## Output

```text
reports/nexus_cell_context_bridge_latest.json
state/nexus_cell/context_bridge_state_latest.json
```

## Boundary

```text
No execution.
No backend enablement.
No network use.
No secret exposure.
No git mutation.
No rollback claim.
No file contents embedded by default.
```

## Law

```text
No shadow receipt without context bridge.
No model handoff without bounded refs.
No whole-repo dump when a context bridge is sufficient.
```
