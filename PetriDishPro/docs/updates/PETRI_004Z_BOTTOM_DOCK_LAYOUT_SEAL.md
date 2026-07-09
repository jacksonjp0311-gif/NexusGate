# PETRI 004Z - Bottom Dock Layout Seal

## Wound
The lower dashboard became visually fragmented after the metric-card and preset-card work:

- Metrics panel overflowed at the bottom-left.
- Particle State / Registry Receipt was cramped.
- Metric charts had horizontal scrollbars.
- Emergent Conditions appeared cut off and could duplicate.
- The lower dashboard did not read as one clean control surface.

## Patch
004Z adds a renderer-side bottom dock layout seal:

- fixed bottom dashboard dock,
- clean five-panel order,
- one Emergent Conditions panel,
- readable receipt rows when raw JSON is present,
- hidden horizontal overflow,
- compact panel sizing.

## Claim boundary
UI layout only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
