# PETRI 005A - Bottom Row No Scroll Seal

## Wound
004Z fixed some bottom dashboard grouping but overcorrected into a fixed dock. That created:

- a huge empty vertical gap between microscope and bottom panels,
- internal scrollbars inside every bottom panel,
- a dock that looked detached from the app.

## Patch
005A overrides 004Z without touching simulation or registry data:

- bottom dock becomes normal document flow, not fixed-bottom,
- body padding-bottom is removed,
- panel scrollbars are hidden,
- Metrics and Emergent Conditions are compacted into visible cards,
- Particle State / Registry Receipt remains human-readable,
- bottom row sits directly below the microscope row.

## Claim boundary
UI layout only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
