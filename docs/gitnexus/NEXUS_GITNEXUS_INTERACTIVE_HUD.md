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

## v0.3.2P hard bridge lineage repair

v0.3.2P creates missing compatibility bridge lineage files when absent and
restores ordered bridge links `a -> b -> c -> d`. GITNEXUS remains loaded from
head with defer and the runtime watchdog remounts the mini graph dock if later
renderer scripts reshape the HUD.

## v0.3.2Q active conversation bridge contract

The active conversation output bridge is now `v0.2.1f` only. Older bridge files
may remain in the repository as history/compatibility artifacts, but they are
not linked in `index.html`. This matches the v021f single-active-bridge test.
GITNEXUS remains loaded from head with defer and is isolated from the body tail.

## v0.3.3 exact-style mini mirror dock

The mini GITNEXUS surface now uses a full mirror-HUD composition instead of a
small graph card. It fills the left dock area with a scaled-down header,
control row, explorer, graph field, recommendation block, selected-node block,
bottom status strip, and a full-width OPEN GITNEXUS HUD button.

## v0.3.5 geometric mini dock

The broken exact-mini-mirror overlay is removed. The mini GITNEXUS dock is now a
simple geometric codegraph visual like the Neural Activity panel: header, OPEN
button, and one large animated geometry canvas. The full popup remains the
interactive graph surface. Toolbar labels are sanitized to ASCII at runtime.

## v0.3.6 flicker fix

The mini GITNEXUS dock now mounts as a singleton. Repeated remount loops and
duplicate dock creation are removed. The mini dock uses one animation loop, one
instance, duplicate cleanup, and resize debouncing to prevent flicker or triple
box rendering.
