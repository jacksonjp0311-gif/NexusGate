# NEXUS Embedded PetriDishPro Bridge

PetriDishPro is embedded inside the NEXUS GATE repository as `PetriDishPro/`.

NEXUS may read PetriDishPro's latest deterministic simulation receipt for the Electron mini preview and may open the PetriDishPro Electron microscope HUD from this embedded source tree.

The bridge is intentionally narrow:

- Mini preview reads `reports/bio/petri_particle_state_latest.json`.
- Mini preview reads latest run `cells.json` and `particles.json`.
- Open launches the embedded PetriDishPro Electron renderer.
- PetriDishPortal points to the embedded `PetriDishPro/` root.

NEXUS must not depend on an outside PetriDishPro source tree after this bridge. The repository copy is the source for NEXUS wiring.

Boundary: deterministic simulation evidence only. No wet-lab authority, clinical authority, treatment guidance, species-identification authority, or autonomous mutation authority is granted.
