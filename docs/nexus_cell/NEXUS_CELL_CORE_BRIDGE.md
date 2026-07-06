# NexusCell Core Bridge

Version: v0.8.7

## Purpose

The NexusCell Core Bridge is the first real NexusCell code bridge.

It converts an intent into:

```text
planner decision
context bridge
NexusCell core contract
read-only bridge packet
handoff target
```

## CLI

```powershell
python -m nexus_gate.nexus_cell.bridge --root . --intent "inspect docs only" --json
.\scripts\nexus.ps1 cell-bridge -Tag "inspect docs only"
```

## Outputs

```text
reports/nexus_cell_bridge_packet_latest.json
state/nexus_cell/bridge_state_latest.json
```

## Contract Fields

```text
cell_contract_id
cell_phase
active_capabilities
blocked_operations
required_authority
human_authorization_required
context_bridge_hash
bridge_packet_id
```

## Boundary

```text
No execution.
No backend enablement.
No process spawn.
No host mount.
No network use.
No secret exposure.
No git mutation.
No rollback claim.
No self-authorization.
```

## Law

```text
No bridge without planner.
No bridge without context.
No bridge without contract.
No contract without boundary.
No mutation from bridge alone.
```
