# PETRI 006J2 â€” Hard Dashboard Panel Override

## Status

Corrective dashboard override added.

## Why

006J was too conservative. It did not replace the actual cramped bottom panels in the live layout, so Metric Charts and Emergent Conditions still looked like tiny placeholder tiles.

006J2 force-targets the visible bottom panels and renders readable rows.

## Added files

- `electron/renderer/dashboardHardOverride006J2.js`
- `electron/renderer/dashboardHardOverride006J2.css`
- `tests/test_dashboard_hard_override_006j2.py`

## Patched file

- `electron/renderer/index.html`

## Behavior

- Metric Charts become readable horizontal trend rows.
- Emergent Conditions become readable condition rows.
- The panel replacement is display-only.
- Simulation math is unchanged.
- The rest of the UI is left intact.

## Boundary

PetriDishPro remains an educational simulation. This layer is not a wet-lab protocol, clinical system, diagnostic system, dosing engine, antimicrobial susceptibility test, species identification tool, treatment guide, or biosafety system.

## Next gate

006K should stop parsing visible text and bind dashboard data directly to explicit run-state JSON.
