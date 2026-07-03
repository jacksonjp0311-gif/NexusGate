# NEXUS GATE v0.2.9 TUI Snapshot Bridge

The TUI snapshot now carries the same core evidence orientation as the interconnect console.

## Command

```text
/snapshot
```

## Output

```text
reports/tui/nexus_tui_snapshot_latest.html
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

## Boundary

The snapshot is evidence orientation only. It must not mutate graph state, self-authorize, bypass evolve, or claim proof from graph visibility.
