# PetriDishPro / Organism Gate

![Organism Gate entry point](docs/assets/organism-gate-entrypoint.svg)

**PetriDishPro** is a cyberpunk live-microscope simulation platform for exploring educational organism cards, preset-driven microbial ecosystems, population dynamics, particle behavior, registry receipts, metric dashboards, and a Drug Lab HUD for interaction modeling.

The project is built around a strict claim boundary:

> PetriDishPro is an educational simulation environment. It is not a wet-lab protocol, diagnostic tool, dosing engine, susceptibility test, treatment guide, clinical system, or biosafety system.

## What it does

PetriDishPro combines:

- a live Electron microscope HUD,
- source-gated organism cards,
- preset-driven simulation modes,
- population curves,
- density maps,
- particle-state receipts,
- metric cards,
- emergent condition cards,
- a Drug Lab HUD for educational interaction proxies,
- validation tests and run receipts.

## Entry point

The main entry point is **Organism Gate**, a terminal menu that opens the HUD, runs presets, validates the project, and opens artifacts.

```text
ORGANISM GATE | PETRI DISH PRO

models simulate -> humans validate -> receipts govern claims

[1] Open Electron Microscope HUD
[2] Run Microbial Competition
[3] Run Antibiotic Selection
[4] Run Cellular Tissue Interaction
[5] Validation Tests
[6] Latest Run Receipt
[7] Open Artifact Folder
[8] Roadmap
[Q] Quit
```

See [`docs/ENTRYPOINT.md`](docs/ENTRYPOINT.md) for the full entry-point contract.

## Quick start

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/jacksonjp0311-gif/PetriDishPro.git
cd PetriDishPro
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Launch the Organism Gate menu from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\ORGANISM_GATE.ps1
```

Alternative Windows launcher:

```powershell
.\START_ORGANISM_GATE.bat
```

## Validation

Run the validation suite before publishing claims:

```powershell
python -m unittest discover -s tests
```

Expected state:

```text
Ran 37 tests
OK
```

## Tool capabilities

| Capability | Description |
| --- | --- |
| Open Electron Microscope HUD | Launches the visual simulation interface. |
| Run Microbial Competition | Runs the default multi-organism competition scenario. |
| Run Antibiotic Selection | Runs an educational antibiotic-pressure scenario. |
| Run Cellular Tissue Interaction | Runs a tissue-interaction proxy scenario. |
| Organism Registry | Displays selectable organism cards and behavior metadata. |
| Drug Lab HUD | Opens a red cyber HUD for educational drug-card interaction proxies. |
| Validation Tests | Runs the test suite and static contracts. |
| Latest Run Receipt | Opens the latest run receipt/artifact state. |
| Artifact Folder | Opens generated outputs and receipts. |
| Roadmap | Opens project direction and next engineering steps. |

See [`docs/TOOL_CAPABILITIES.md`](docs/TOOL_CAPABILITIES.md) for the full capability map.

## Interface surfaces

- **Experiment panel:** preset selection, run controls, grid/step settings, microscope view controls, field layer selection.
- **Microscope viewport:** live organism/particle rendering.
- **Organism Registry:** population curves and organism cards.
- **Bottom dashboard:** metrics, density map, particle state, metric charts, emergent conditions.
- **Drug Lab HUD:** educational drug interaction card surface.
- **Receipts:** run identity, selected organisms, preset, and validation state.

## Project structure

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for the generated structure guide.

## Development status

Current focus areas:

- stable Organism Gate entry point,
- professional repository publication,
- stable HUD/registry layout,
- registry-driven organism and drug selectors,
- event-bus integration for Drug Lab interactions,
- stronger behavior models for motility, adaptation, biofilm pressure, predator/prey logic, and drug-gradient proxies.

## Claim boundary

PetriDishPro can visualize simplified biology-inspired dynamics, but it does not provide:

- clinical advice,
- medical diagnosis,
- treatment guidance,
- dosing recommendations,
- wet-lab protocols,
- antimicrobial susceptibility results,
- antibody-affinity measurements,
- species identification,
- biosafety instructions.

Use it as an educational simulation and visualization platform only.

## License

This repository is published under the MIT License.

## Public smoke check

Before publishing a release or sharing a build, run:

```powershell
./scripts/public_smoke_check.ps1 -NoNodeInstall
```

For a launcher attempt from a public clone:

```powershell
./scripts/launch_organism_gate.ps1
```

Release checklist and beta notes:

- [`docs/PUBLIC_RELEASE_CHECKLIST.md`](docs/PUBLIC_RELEASE_CHECKLIST.md)
- [`docs/releases/v0.6.0-beta.md`](docs/releases/v0.6.0-beta.md)
- [`docs/ROADMAP_PRO_LEVEL.md`](docs/ROADMAP_PRO_LEVEL.md)
