# NEXUS GATE v0.3.7 Interface Adapter Contract

Every interface is an adapter over the same NEXUS core. The UI never owns the logic.

```text
one engine
many interfaces
same gates
same evidence
same feedback memory
same authority boundary
```

## Authority Levels

```text
read_only
feedback_write_only
operation_packet_write
allowlisted_lane_request
human_authorized_patch
blocked
```

No interface may declare autonomous mutation authority.

## Required Adapter Fields

Each interface adapter declares:

```text
interface_id
surface_type
read_surfaces
write_surfaces
allowed_commands
blocked_actions
authority_level
handoff_format
reflection_format
required_gates
claim_boundary
```

## Interfaces

The canonical machine-readable contract is:

```text
state/interface_adapter_contract_index.v0.3.7.json
```

It declares these interfaces:

```text
powershell_cli
powershell_tui
electron_hud
chatgpt_handoff
codex_handoff
future_browser_dashboard
future_local_agent
```

## Boundary

Interface adapters expose governed actions and evidence. They do not create new authority, bypass evolve, run arbitrary shell commands, access secrets, write external APIs, or prove production readiness.
