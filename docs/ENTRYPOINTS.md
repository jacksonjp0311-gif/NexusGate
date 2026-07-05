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


## GitHub Repository

```text
https://github.com/jacksonjp0311-gif/NexusGate
```

## Reflective Repair Loop

```powershell
.\scripts\nexus_reflective_repair.ps1 -Issue "Summarize the failing test and recommend a bounded repair" -CallModel
```

The loop calls NEXUS DEEP/Mistral through the local NN router, prints recommendation context, asks Y/N, and only applies a bounded repair when the human approves.
