# PETRI 005T - Control Spacing and Card Menus

## Wound
A slight overlap remained in the top-right control pod after 005S. The user also requested explicit aligned selectors for all organism cards and drug cards.

## Patch
005T applies a narrow UI-only repair:

- reduces and regularizes top-right control spacing,
- keeps Drug Lab slightly wider than the other buttons so the label fits cleanly,
- injects an aligned organism card selector menu,
- injects an aligned drug card selector menu,
- selecting an organism card scrolls to it and toggles its checkbox on if needed,
- selecting a drug card scrolls to it and activates it.

## Claim boundary
UI alignment and selection-shell only. No wet-lab, dosing, susceptibility, efficacy, diagnostic, treatment, or biosafety claim is created.
