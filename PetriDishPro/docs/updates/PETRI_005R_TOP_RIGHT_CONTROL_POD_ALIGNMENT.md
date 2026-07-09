# PETRI 005R - Top Right Control Pod Alignment

## Wound
After 005Q/005Q2 recovered the app, the top-right control pod was visually uneven. The Drug Lab button existed but the row needed surgical alignment.

## Patch
005R adds a last-loaded, narrow repair layer:

- finds the existing Capture / Drug Lab / Pause / Reset / State buttons,
- normalizes their labels,
- assigns a stable top-control pod class,
- orders the buttons as Capture, Drug Lab, Pause, Reset, State,
- forces equal button width and height,
- keeps the repair scoped to the top-right controls.

## Claim boundary
UI alignment only. No wet-lab, diagnostic, treatment, dosing, susceptibility, affinity, species-ID, clinical, or biosafety claim is added.
