# NexusShell Full-Scope Operator Shell

Version: v0.8.6

## Purpose

NexusShell is the Python-native operator shell for NexusGate.

It binds the current organs into one no-execution command center:

```text
NexusGate compiler
NexusCell planner
NexusCell context bridge
Failure Doctor
Desktop Portal
Compact PowerShell command surface
```

## Commands

```text
status
rehydrate
compile
doctor
cell-plan
cell-context
handoff
help
```

## CLI

```powershell
python -m nexus_gate.nexus_shell.shell --root . --command status --intent "inspect docs only" --json
.\scripts\nexus.ps1 shell -Tag "inspect docs only"
```

## Boundary

```text
NexusShell routes and summarizes governed operator lanes only.
It does not execute arbitrary commands.
It does not enable backends.
It does not expose secrets.
It does not use network.
It does not mutate git.
It does not claim rollback.
It does not self-authorize.
```

## Output

```text
reports/nexus_shell_packet_latest.json
state/nexus_shell/shell_state_latest.json
```

## Law

```text
No shell command without lane.
No lane without boundary.
No handoff without context bridge.
No mutation without human authorization.
```
