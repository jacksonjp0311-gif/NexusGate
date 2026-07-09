# PETRI 006J â€” Dashboard Readability Upgrade

## Status

Dashboard readability layer added.

## Why

The v0.6I dedupe repair fixed repeated Drug Card options, but the lower dashboard still needed a stronger redesign:

- Metric Charts were cramped into narrow cards.
- Emergent Conditions were clipped and hard to understand.
- The panel needed readable trend rows and condition rows instead of tiny truncated boxes.

## Added files

- `electron/renderer/dashboardReadability006J.js`
- `electron/renderer/dashboardReadability006J.css`
- `tests/test_dashboard_readability_006j.py`

## Patched file

- `electron/renderer/index.html`

## Behavior

006J renders display-only dashboard replacements inside the existing panels:

- Metric Charts become horizontal trend rows.
- Emergent Conditions become readable condition rows.
- The rest of the app remains untouched.
- No simulation math is changed.
- A receipt event confirms the display layer is active.

## Boundary

PetriDishPro remains an educational simulation. This layer is not a wet-lab protocol, clinical system, diagnostic system, dosing engine, antimicrobial susceptibility test, species identification tool, treatment guide, or biosafety system.

## Next gate

006K should bind these dashboard readouts to explicit run-state JSON instead of parsing visible text.
