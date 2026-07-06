# NexusCell Read-Only Planner

Version: v0.8.4C

## Purpose

The NexusCell planner is the first Python-native package surface for the execution containment organ.

It does not execute code.

It converts human or model-generated intent into:

```text
intent
-> capability vector
-> risk score
-> authority decision
-> route mode
-> report/state evidence
```

## Command

```powershell
python -m nexus_gate.nexus_cell.plan --root . --intent "inspect docs only" --json
.\scripts\nexus.ps1 cell-plan -Tag "inspect docs only"
```

## Boundary

```text
No execution backend.
No subprocess runner.
No sandbox claim.
No rollback claim.
No secret exposure.
No git mutation.
No self-authorization.
```

## Output

```text
reports/nexus_cell_plan_latest.json
state/nexus_cell/planner_state_latest.json
```

## Law

```text
Plan before invoke.
Score before authority.
Authority before containment.
Receipt before claim.
Ledger before compounding.
```
