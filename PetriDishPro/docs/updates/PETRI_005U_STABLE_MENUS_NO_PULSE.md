# PETRI 005U - Stable Menus No Pulse

## Wound
005T added the right idea, but it rebuilt the selector rows every cycle. That made the UI pulse/flicker.

## Patch
005U makes the selector layer stable:

- removes the pulsing `controlSpacingAndMenus005T.js` binding,
- adds `stableMenusNoPulse005U.js`,
- only creates selector rows if missing or if the card list signature changes,
- keeps a short bootstrap interval, then stops,
- uses a debounced mutation observer instead of constant row recreation,
- suppresses pulse/flash animation on selector rows,
- preserves the top-right spacing repair and the organism/drug selector menus.

## Claim boundary
UI stability and selector-shell only. No wet-lab, dosing, susceptibility, efficacy, diagnostic, treatment, or biosafety claim is created.
