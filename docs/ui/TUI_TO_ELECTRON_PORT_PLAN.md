# NEXUS GATE TUI to Electron Port Plan

The PowerShell TUI is the proof surface for the future Electron operator shell.

## Current Bridge

```text
PowerShell TUI
  -> governed NEXUS lane
  -> report/state/log evidence
  -> AI handoff export
  -> HTML snapshot
  -> future Electron presentation
```

## Required TUI Commands

```text
/ai
/copy
/snapshot
/electron
```

## Electron Read Surfaces

```text
state/ai_feedback_context_latest.json
docs/feedback/FEEDBACK_LOG.md
docs/feedback/operator_packets/*.json
reports/nexus_feedback_interface_report_latest.json
reports/nexus_self_healing_report_latest.json
reports/tui/nexus_tui_ai_handoff_latest.txt
reports/tui/nexus_tui_snapshot_latest.html
```

## Electron Allowlist

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

## Blocked Actions

```text
arbitrary shell commands
external API writes
secret access
self-authorization
memory promotion without evidence
ungated repo mutation
```

## Design Law

The operator surface may make governed actions visible and selectable. It may not become the operator. It may not self-authorize. It may not bypass gates.

Boundary: this bridge plan is local development evidence only. It does not prove correctness, safety, security, production readiness, or autonomous authority.
