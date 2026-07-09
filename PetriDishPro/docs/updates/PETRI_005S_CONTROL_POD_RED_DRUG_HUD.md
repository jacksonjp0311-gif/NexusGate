# PETRI 005S - Control Pod and Red Drug HUD

## Wound
The top-right control pod still looked uneven after the safe recovery work, and the user requested the Drug Lab panel be rendered as a red semi-transparent HUD.

## Patch
005S applies a surgical UI-only repair:

- reorders top controls as Capture, Drug Lab, Run or Pause, Reset, State,
- forces consistent button heights,
- widens Drug Lab so it fits cleanly,
- applies a red semi-transparent visual treatment to the drug interaction HUD,
- keeps the repair isolated to top-right controls and drug HUD surfaces.

## Claim boundary
UI alignment and appearance only. No wet-lab, diagnostic, treatment, dosing, efficacy, susceptibility, or biosafety claim is added.
