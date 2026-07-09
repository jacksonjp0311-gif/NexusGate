# PETRI 006H â€” Event Bus UI Wiring

## Status

Non-destructive UI wiring layer added.

## Purpose

006H connects existing visible UI controls to the 006G event bus without rebuilding the interface.

The gate does not remove legacy handlers. It only adds canonical event emissions around the current UI.

## Added file

- `electron/renderer/eventBusWiring006H.js`

## Patched file

- `electron/renderer/index.html`

## Events wired

- `organism:selected`
- `drug:selected`
- `drug:injected`
- `preset:changed`
- `simulation:step`
- `receipt:written`

## Runtime surface

- `window.PetriEventBusWiring006H`

## Safety model

This is a UI-state bridge only. Drug injection is represented as an educational interaction proxy.

PetriDishPro remains an educational simulation. This layer is not a wet-lab protocol, clinical system, diagnostic system, dosing engine, antimicrobial susceptibility test, species identification tool, treatment guide, or biosafety system.

## Next gate

006I should replace heuristic selector inference with explicit registry IDs and visible state receipts.
