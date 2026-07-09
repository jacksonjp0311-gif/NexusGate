# PETRI 005H - Stable Bottom Owner Seal

## Wound
005G fixed the PowerShell failure and added a fill override, but that created a second runtime placement loop. The 005D overlay loop and 005G fill loop fought each other, so the dashboard flickered between small and large sizes.

## Patch
005H removes the second owner:

- unbinds `bottomFillViewportSeal.js`,
- keeps exactly one `bottomSingleLayerSeal.js`,
- patches `bottomSingleLayerSeal.js` so its own `place()` function uses:
  - `top = microscope bottom + 8px`,
  - `bottom = 8px`,
  - `height = auto`.

## Claim boundary
UI layout only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
