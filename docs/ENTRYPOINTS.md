# NEXUS GATE Entrypoints

## Desktop Entry Portal

The Desktop Entry Portal is the fastest human doorway into the local operator surfaces.

## Windows PowerShell

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\desktop\open_nexus_gate_console.ps1

.\scripts\nexus.ps1 ui
.\scripts\nexus.ps1 tui
.\scripts\nexus.ps1 status
.\scripts\nexus.ps1 evolve
.\scripts\nexus.ps1 reflect
.\scripts\nexus.ps1 domain
.\scripts\nexus.ps1 electron-preflight
```

## Bash / Git Bash / WSL / Linux / macOS

```bash
bash scripts/nexus.sh status
bash scripts/nexus.sh evolve
bash scripts/nexus.sh reflect
bash scripts/nexus.sh domain
bash scripts/nexus.sh electron-env
bash scripts/nexus.sh electron-preflight
```

## GitHub / README / Docs Submenu

The Desktop Entry Portal includes a GitHub / README / Docs submenu for fast navigation:

```text
Open GitHub repository
Open GitHub README
Open docs/ENTRYPOINTS.md
Open docs/versioning/NEXUS_CHANGELOG.md
Open local README.md
Open local docs folder
```

## GitHub Repository

```text
https://github.com/jacksonjp0311-gif/NexusGate
```

## Electron HUD

```powershell
cd electron
npm install
npm start
npm run smoke
```

## Validation

```powershell
python -m unittest discover -s tests
python -m nexus_gate.compiler --root . --json
```

```text
Portal opens surfaces.
NEX recommends.
Doctor classifies.
Compiler gates.
Human authorizes.
```


## Reflective Repair Loop

```powershell
.\scripts\nexus_reflective_repair.ps1 -Issue "Summarize the failing test and recommend a bounded repair" -CallModel
```

The loop calls NEXUS DEEP/Mistral through the local NN router, prints recommendation context, asks Y/N, and only applies a bounded repair when the human approves.


## Geometric Memory Router

```powershell
Get-Content .\docs\intelligence\NEXUS_GEOMETRIC_MEMORY_ROUTER.md -TotalCount 120
Get-Content .\docs\algorithms\NEXUS_TESSERACT_ALIGNMENT_KERNEL.md -TotalCount 120
Get-Content .\docs\memory\EIMT_RUNTIME_MEMORY_CONTRACT.md -TotalCount 120
Get-Content .\state\nexus_geometric_memory_manifest.v0.8.3.json -Raw
```

Use this entry before changing memory, routing, context slicing, model-role weights, or reflective repair behavior.


## Geometric Runtime Packet

```powershell
python -m nexus_gate.geometric_memory.router --root . --intent "What should we do next?" --json
.\scripts\nexus.ps1 geo -Tag "What should we do next?"
```

```bash
bash scripts/nexus.sh geo "What should we do next?"
```


## Geometric Cleanup

```powershell
python -m nexus_gate.geometric_memory.cleanup --root . --json
.\scripts\nexus.ps1 geo-clean
```

```bash
bash scripts/nexus.sh geo-clean
```

Use cleanup after smoke tests, full-suite runs, or failed scripts that leave generated report residue.



## NexusCell Execution Containment

```powershell
Get-Content .\docs\nexus_cell\NEXUS_CELL_ARCHITECTURE.md -TotalCount 120
Get-Content .\state\nexus_cell\cell_manifest.v0.8.4.json -Raw
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\desktop\open_nexus_gate_console.ps1
```

Desktop Portal access:

```text
[10] NexusCell / Containment -> execution governance doctrine
```

Boundary: NexusCell is doctrine/manifest/UI access only at v0.8.4B. No execution backend is enabled.


## NexusCell Read-Only Planner

```powershell
python -m nexus_gate.nexus_cell.plan --root . --intent "inspect docs only" --json
.\scripts\nexus.ps1 cell-plan -Tag "inspect docs only"
```

Desktop Portal access:

```text
[10] NexusCell / Containment
6. Plan gated invocation (read-only)
```

Boundary: planner emits risk/authority evidence only. It does not execute.
