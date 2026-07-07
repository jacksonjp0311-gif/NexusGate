# NexusGate GITNEXUS Big Nexus HUD v0.2.0

This evolves the GITNEXUS pop-out from a small status panel into a native
NexusGate codegraph explorer inspired by the real GitNexus web app.

The real GitNexus web app has a shell made from:
- top header/search/repo controls,
- left file tree/filter surface,
- central graph canvas,
- right code/chat/detail panel,
- bottom status bar.

NexusGate v0.2.0 ports that interaction pattern without vendoring the React/Vite
application or adding Sigma/Graphology dependencies.

## v0.2.0 surface

- Floating left dock remains in the empty left slot.
- Full HUD opens as a large native NexusGate overlay.
- Central canvas renders hundreds of file nodes.
- Edges are drawn from the Python GITNEXUS report.
- Hot/imported files and changed files are highlighted.
- Search highlights nodes.
- Click node to inspect.
- Right panel shows recommendation, top imported files, selected node.
- Left panel shows codegraph stats, filters, changed files.

## Boundary

Evidence only. No autonomous authority. No shell execution from model output.
No NexusCell policy change. No Mode Selection Green HUD asset changes.
