# PETRI 005C - Authoritative Bottom Overlay

## Wound
005B restored the bottom bar, but the boxes were sized inconsistently and some panels did not load because the layout was still moving older dashboard DOM nodes.

## Patch
005C stops moving old panels and creates one self-rendering bottom overlay:

- Metrics panel renders its own live cards.
- Density Map renders its own canvas.
- Particle State / Registry Receipt renders readable rows.
- Metric Charts render their own mini charts.
- Emergent Conditions renders compact state cards.
- Old bottom dock systems are hidden.

## Claim boundary
UI rendering only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
