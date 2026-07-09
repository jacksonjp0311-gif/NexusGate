# PETRI 005G - Safe Bottom Fill Override

## Wound
005F had the correct visual intent but failed in PowerShell before writing the patch because the `-replace` operator was called with an invalid argument shape.

## Patch
005G avoids PowerShell replacement entirely. It adds a separate last-loaded renderer script:

- `bottomFillViewportSeal.js`

This script keeps the 005D single-layer overlay, then forces it to fill from the microscope bottom to 8px above the viewport bottom.

## Claim boundary
UI layout only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
