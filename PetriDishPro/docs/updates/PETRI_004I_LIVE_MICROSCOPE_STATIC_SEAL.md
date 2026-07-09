# PETRI 004I â€” Live Microscope Static Seal

## Wound
004H patched the compact live microscope design, but unit tests failed with one remaining static renderer marker wound. The runtime design was present; the static compatibility surface was incomplete for older 004C/004H tests.

## Patch
004I adds a harmless compatibility surface without changing the visual design:

- `visual_contract` marker in `app.js`,
- `drawAmoeba` alias beside `drawAmoeboid`,
- schema adapter compatibility markers,
- explicit continuous animation marker,
- preserved compact topbar / LIVE SIM design.

## Claim boundary
This is a static compatibility seal only. It does not alter biology or scientific claim level.
