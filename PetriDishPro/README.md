# PetriDishPro NEXUS Root

PetriDishPro is interlinked into NEXUS GATE as an external organism-gate workbench.

Canonical external root:

```text
C:\Users\jacks\OneDrive\Desktop\PetriDishPro
```

NEXUS owns this bridge folder. PetriDishPro owns its simulation code, Electron microscope HUD, artifacts, reports, and organism gate.

## NEXUS Surfaces

- Electron mini HUD reads the latest Petri particle-state report.
- Electron `PETRIDISHPRO` panel opens the full PetriDishPro microscope HUD in a separate maximized window.
- Spiral Core Portal exposes `PetriDishPortal`.

## Read Surfaces

- `reports/bio/petri_particle_state_latest.json`
- `artifacts/bio/runs/<run_id>/cells.json`
- `artifacts/bio/runs/<run_id>/particles.json`
- `reports/bio/*.json`
- `config/*.json`

## Write / Execute Surfaces

PetriDishPro remains the authority for its own bounded runs. NEXUS may launch the Petri Electron surface and fixed Petri IPC handlers only.

## Blocked Actions

- no arbitrary shell through NEXUS
- no clinical or medical authority
- no wet-lab instruction authority
- no species-identification claim
- no autonomous mutation of Petri or NEXUS repos
- no promotion of simulation to empirical proof

## Claim Boundary

PetriDishPro previews are deterministic simulation evidence only. They are not microscopy evidence, clinical evidence, treatment guidance, species identification, biosafety evidence, or proof of biological truth.
