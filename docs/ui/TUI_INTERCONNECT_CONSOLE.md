# NEXUS GATE v0.2.8 TUI Interconnect Console

The PowerShell TUI now exposes the governed graph as an operator-readable console.

## Command

```text
/graph
```

Compatibility alias:

```text
/interconnect
```

## Displays

```text
graph status
graph version
node count
edge count
graph hash prefix
feedback health
evidence pressure
next action
compiler/check rows
first governed route edges
placeholder or missing evidence paths
```

## Boundary

The graph view is evidence orientation. It does not prove correctness, production readiness, safety, scientific validity, model validity, or autonomous authority.

## Snapshot Bridge

The `/snapshot` command also writes the graph status, node and edge counts, check rows, placeholder evidence paths, and next action into:

```text
reports/tui/nexus_tui_snapshot_latest.html
```

This HTML file is the first Electron mock surface. It is still read-only evidence orientation.
