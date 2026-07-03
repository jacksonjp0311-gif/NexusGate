# NEXUS GATE v0.3.0 TUI Surface State

The TUI can now export a compact machine-readable surface state for Electron and future dashboard views.

## Command

```text
/surface
```

## Output

```text
reports/tui/nexus_tui_surface_latest.json
```

## Contents

```text
health score
evidence pressure
dominant pressure
next action
graph status
graph version
node and edge counts
graph checks
missing evidence paths
launch commands
read surfaces
blocked actions
claim boundary
```

## Boundary

The surface state is read-only evidence orientation. It does not mutate graph state, self-authorize, bypass evolve, run arbitrary shell commands, or prove correctness, safety, scientific validity, model validity, production readiness, or autonomous authority.
