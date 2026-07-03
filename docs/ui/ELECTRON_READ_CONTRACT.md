# NEXUS GATE v0.3.2 Electron Read Contract

Electron is a future presentation/operator surface. It must consume existing NEXUS evidence and may only request governed lanes.

## Read Surfaces

```text
state/ai_feedback_context_latest.json
docs/feedback/FEEDBACK_LOG.md
docs/feedback/operator_packets/*.json
reports/nexus_feedback_interface_report_latest.json
reports/nexus_self_healing_report_latest.json
reports/tui/nexus_tui_ai_handoff_latest.txt
reports/tui/nexus_tui_snapshot_latest.html
reports/tui/nexus_tui_surface_latest.json
```

## Allowlisted Commands

```text
evolve
interface
feedback
heal
status
compact
interconnect
runtime
pack
```

## Required Pair

```text
/snapshot
  -> reports/tui/nexus_tui_snapshot_latest.html
  -> reports/tui/nexus_tui_surface_latest.json
```

## Blocked Actions

```text
arbitrary_shell_commands
external_api_write
secret_access
self_authorize
memory_promotion_without_evidence
ungated_repo_mutation
mutate_graph_state
bypass_evolve
```

## Boundary

This contract is a local development gate for a future Electron surface. It does not build Electron, grant shell authority, prove correctness, prove safety, validate production readiness, or authorize autonomous action.
