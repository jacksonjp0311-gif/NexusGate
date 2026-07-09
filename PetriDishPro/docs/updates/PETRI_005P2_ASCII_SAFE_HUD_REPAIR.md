# PETRI 005P2 - ASCII Safe HUD Repair

## Wound
005P failed before it executed because a mojibake dash token broke PowerShell parsing.

## Patch
005P2 is fully ASCII-safe at the PowerShell layer and performs the intended visual repair:

- cleans the base Drug Lab labels,
- removes common mojibake/unicode tokens from `drugInjectionLab005O.js`,
- adds `drugInjectionHudFix005P2.js` as the last-loaded repair layer,
- removes any broken `drugInjectionHudFix005P.js` binding,
- forces the HUD above all layers,
- makes the HUD draggable by its header,
- adds Center / Dock Right / Wide controls,
- hides ghosted right-panel content,
- tightens collapsed organism cards in the right lane.

## Claim boundary
UI repair only. No wet-lab, diagnostic, treatment, dosing, susceptibility, affinity, species-ID, clinical, or biosafety claim is added.
