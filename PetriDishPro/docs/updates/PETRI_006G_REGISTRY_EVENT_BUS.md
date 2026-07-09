# PETRI 006G â€” Registry Event Bus Foundation

## Status

Foundation layer added.

## Purpose

006G adds a non-destructive event bus and registry selector bridge for PetriDishPro.

The goal is to stop future organism/drug/preset behavior from depending on DOM inference alone. Existing UI remains intact, but future features can now use a canonical event surface.

## Added files

- `electron/renderer/petriEventBus006G.js`
- `electron/renderer/registrySelectors006G.js`
- `tests/test_registry_event_bus_006g.py`

## Canonical events

- `organism:selected`
- `drug:selected`
- `drug:injected`
- `preset:changed`
- `simulation:step`
- `receipt:written`
- `registry:loaded`

## Runtime surfaces

- `window.PetriEventBus`
- `window.PetriRegistrySelectors006G`

## Boundary

PetriDishPro remains an educational simulation. This layer is not a wet-lab protocol, clinical system, diagnostic system, dosing engine, antimicrobial susceptibility test, species identification tool, treatment guide, or biosafety system.

## Next gate

006H should wire existing UI selectors and Drug Lab controls into the event bus without breaking current rendering.
