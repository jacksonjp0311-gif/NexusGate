# PETRI 006I â€” Drug Dedupe + Dashboard Polish

## Status

UI repair layer added.

## Why

After 006G/006H, the event bus foundation worked, but the visible Drug Cards selector could show duplicate drug options when multiple registries contributed overlapping drug cards.

The lower dashboard also needed readability improvement:

- Metric Charts cards were too narrow and hard to use.
- Emergent Conditions cards were cramped and truncated.
- Duplicate drug card options reduced trust in the registry layer.

## Added files

- `electron/renderer/registryDedupeDashboard006I.js`
- `electron/renderer/dashboardPolish006I.css`
- `tests/test_drug_dedupe_dashboard_006i.py`

## Patched file

- `electron/renderer/index.html`

## Behavior

006I is non-destructive. It does not replace the existing UI and does not remove legacy handlers.

It adds:

- drug select option deduplication
- registry array dedupe helper
- dashboard card readability classes
- metric chart panel labeling
- emergent condition panel labeling
- a receipt event confirming the polish layer is active

## Boundary

PetriDishPro remains an educational simulation. This layer is not a wet-lab protocol, clinical system, diagnostic system, dosing engine, antimicrobial susceptibility test, species identification tool, treatment guide, or biosafety system.

## Next gate

006J should explicitly bind registry IDs to the drug/organism cards so UI state, receipts, and selected cards all share the same canonical object.
