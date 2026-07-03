# NEXUS GATE v0.2.9 TUI Snapshot Bridge

The TUI snapshot now carries the same core evidence orientation as the interconnect console.

## Command

```text
/snapshot
```

## Output

```text
reports/tui/nexus_tui_snapshot_latest.html
reports/tui/nexus_tui_surface_latest.json
```

## Snapshot Sections

```text
health
evidence pressure
graph status
graph version
node and edge counts
next action
interconnect checks
placeholder evidence paths
bridge surfaces
claim boundary
```

## Purpose

This HTML file is the first Electron mock surface. It gives Electron a read-only target to mirror before any desktop shell is built.

As of v0.3.1, `/snapshot` also refreshes the companion JSON surface state so Electron/dashboard consumers can pair the human HTML view with the machine-readable state export from the same operator action.

## Boundary

The snapshot is evidence orientation only. It must not mutate graph state, self-authorize, bypass evolve, or claim proof from graph visibility.
