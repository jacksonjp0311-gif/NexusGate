# NexusGate GITNEXUS Interactive HUD v0.3.1

v0.3.1 finalizes the mini dock and keeps the full interactive explorer.

## Mini dock

The main NexusGate dock is intentionally only:

```text
GITNEXUS header
animated graph preview
Open GitNexus HUD button
```

No file/symbol/edge/risk cards render in the main dashboard slot.

## Full HUD controls

- Drag canvas: pan
- Mouse wheel: zoom
- Alt-drag: rotate
- Turn / left rotate / right rotate buttons
- Drag node: move/pin node
- Click node: inspect
- Search: highlight files/symbols
- Toggle edges, labels, changed-only, symbols

## Boundary

Evidence only. No autonomous authority. No shell execution from model output.
No NexusCell policy change. No Mode Selection Green HUD asset changes.

## v0.3.1K body-tail hygiene

The GITNEXUS HUD script is loaded from `<head>` with `defer`. This keeps the
existing renderer body-tail script order intact, including the metrics HUD and
mode-selection assets. The dock still mounts after DOM parsing.

## v0.3.1M conversation bridge lineage

The conversation output bridge lineage remains linked as `v0.2.1a`, `v0.2.1b`,
and `v0.2.1c`. GITNEXUS does not own or collapse that lineage. GITNEXUS is
loaded from head with `defer` and does not pollute the metrics/body tail.
