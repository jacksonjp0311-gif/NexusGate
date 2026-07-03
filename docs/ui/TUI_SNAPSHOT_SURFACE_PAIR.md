# NEXUS GATE v0.3.1 TUI Snapshot Surface Pair

The TUI now pairs the operator-facing HTML snapshot with the machine-readable JSON surface state.

## Command

```text
/snapshot
```

## Paired Outputs

```text
reports/tui/nexus_tui_snapshot_latest.html
reports/tui/nexus_tui_surface_latest.json
```

## Purpose

Electron and future dashboard consumers can read both surfaces after one operator action:

```text
human view: reports/tui/nexus_tui_snapshot_latest.html
machine view: reports/tui/nexus_tui_surface_latest.json
```

The TUI still does not own logic. The paired export only mirrors compiled feedback/interconnect evidence and launch commands.

## Boundary

The paired export is read-only evidence orientation. It does not mutate graph state, self-authorize, bypass evolve, run arbitrary shell commands, or prove correctness, safety, scientific validity, model validity, production readiness, or autonomous authority.
