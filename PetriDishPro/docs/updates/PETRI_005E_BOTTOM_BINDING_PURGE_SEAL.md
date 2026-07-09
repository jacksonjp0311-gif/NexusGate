# PETRI 005E - Bottom Binding Purge Seal

## Wound
005D wrote the correct single-layer overlay, but the previous regex did not remove every old bottom script binding from `index.html`.

Remaining old bindings:
- `bottomLayoutSeal.js`
- `bottomDockVisibleSeal.js`

## Patch
005E performs a stronger purge:
- removes every script tag that references old bottom layout scripts,
- removes any residual line containing those old binding names,
- re-adds exactly one `bottomSingleLayerSeal.js` binding,
- adds a hard CSS hide for old dock containers.

## Claim boundary
UI ownership only. No simulation, organism, drug, antibody, clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claim is changed.
