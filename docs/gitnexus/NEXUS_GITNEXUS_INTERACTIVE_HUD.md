# NexusGate GITNEXUS Interactive HUD v0.3.0

v0.3.0 turns the small dock into a mini GitNexus UI and upgrades the full HUD
into an interactive graph explorer.

## Borrowed interaction pattern

The real GitNexus web app uses:
- search/header controls,
- file tree/filter panels,
- graph canvas,
- selected-node focus,
- zoom/reset/layout controls,
- highlighted/animated graph states.

NexusGate ports the interaction pattern into a dependency-free native Electron
renderer overlay.

## New behavior

Small dock:
- mini animated codegraph canvas,
- file/symbol/edge/risk stats,
- full HUD open button.

Full HUD:
- drag canvas to pan,
- wheel to zoom,
- Alt-drag or Turn button to rotate,
- drag nodes to reposition/pin,
- click nodes to inspect,
- search files/symbols,
- toggle edges, labels, changed-only, and symbols,
- render file nodes, symbol nodes, import edges, and defines edges,
- track changed files, hot imported files, connected nodes, and selected node details.

## Boundary

Evidence only. No autonomous authority. No shell execution from model output.
No NexusCell policy change. No Mode Selection Green HUD asset changes.
