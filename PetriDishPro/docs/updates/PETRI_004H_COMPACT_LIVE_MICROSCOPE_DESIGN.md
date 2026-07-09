# PETRI 004H â€” Compact Live Microscope Design

## Wound
The interface was too text-heavy at the top and the visual identity still did not feel like a live microscope. The supplied reference emphasized a compact topbar, central live simulation status, action buttons, side controls, continuous canvas animation, and capture as a separate action.

## Patch
004H rewrites the Electron renderer into a compact live microscope cockpit:

- reduced topbar text,
- central LIVE SIM card,
- capture/pause/reset/state action cluster,
- continuous `requestAnimationFrame(loop)` animation,
- capture saves a frame but never controls animation,
- animated host fields, particles, and organism/cell morphology proxies,
- compact left config panel,
- right inspector for curves, cards, archive, and config receipt,
- bottom metrics/density/receipt strip,
- legacy compatibility markers preserved.

## Claim boundary
This is a visual/operator-surface refinement. It does not alter simulation biology, validation level, wet-lab evidence, or scientific claim status.
