# NEXUS GITNEXUS Local HUD v0.5.1

## Decision

The upstream bridge proved useful, but it was the wrong product shape for
NexusGate. It tried to load the hosted GitNexus Web UI and validate a local
GitNexus server. This repository wants a native NexusGate visual codegraph HUD.

## v0.5.1 behavior

- No `gitnexus.vercel.app`
- No `localhost:4747`
- No iframe
- No remote/server bridge
- Mini dock = geometric preview + OPEN only
- Full HUD = local canvas graph
- Pan, zoom, rotate, fit, edge toggle, label toggle, core filter
- Reads local GITNEXUS/state/report JSON when available
- Falls back to deterministic NexusGate graph if JSON shape changes

## Controls

```text
drag                  pan
mouse wheel           zoom
Alt + drag            rotate
Shift + mouse wheel   rotate
FIT                   fit graph
TURN                  rotate graph
EDGES                 toggle edges
LABELS                toggle labels
CORE                  focus core/python files
Ctrl+K                search when HUD is open
Esc                   close HUD
```

## Boundary

Evidence-only. No NexusCell policy change. No shell execution from model output.