# NEXUS GATE Hermes-Style PowerShell TUI

This is a terminal UI inside PowerShell, not a Windows Forms app.

## Launch

```powershell
.\scripts\nexus.ps1 tui
```

or:

```powershell
.\scripts\nexus_tui.ps1
```

## Design Source

The interface follows the Hermes/HRCN operator-surface law:

```text
An operator surface may make governed actions visible and selectable; it may not become the operator.
```

## What It Gives You

```text
Hermes-style terminal shell
Process lane dropdown menu
Chat-like NEXUS> prompt
Colored output
Progress / buffer bar
AI handoff export
Feedback note capture
Operation packet creation
Debug tail viewer
Self-healing lane access
Evolve lane access
```

## Commands

```text
/run evolve
/run interface
/run feedback
/run heal
/run status
/run compact
/run interconnect
/run runtime
/run pack

/note <text>
/packet <summary>
/debug
/ai
/copy
/snapshot
/surface
/electron
/graph
/open-log
/open-context
/menu
/exit
```

## Repo-Changing Actions

The TUI can make bounded repo changes only in feedback/operator surfaces:

```text
/note    -> appends docs/feedback/FEEDBACK_LOG.md
/packet  -> writes docs/feedback/operator_packets/*.json
/run ... -> runs existing governed NEXUS lanes
```

It does not self-authorize runtime mutation, external API writes, memory promotion, or secret access.

## AI Handoff

Use:

```text
/ai
```

Then copy the printed block into ChatGPT/Codex. It includes the latest feedback context, interface report, and self-healing report.

Use:

```text
/copy
```

to write `reports/tui/nexus_tui_ai_handoff_latest.txt` and copy it to the clipboard when available.

Use:

```text
/snapshot
```

to write and open `reports/tui/nexus_tui_snapshot_latest.html`.

The snapshot includes graph status, node and edge counts, interconnect checks, placeholder evidence paths, and next action for the future Electron surface.

Use:

```text
/graph
```

to show the governed interconnect console: graph status, node and edge counts, checks, placeholder evidence paths, and next action.

Use:

```text
/surface
```

to write `reports/tui/nexus_tui_surface_latest.json` for Electron/dashboard consumers.

Use:

```text
/electron
```

to print the future Electron port contract. Electron must consume the same evidence surfaces and only run allowlisted NEXUS lanes.

## Claim Boundary

The TUI is a local operator/debug surface. It does not prove correctness, security, safety, production readiness, or autonomous authority.
