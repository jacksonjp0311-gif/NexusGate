# scripts

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): runtime, validation, evidence, entrypoint
- Sector: scripts
- Version / TTL: NG-RHP-NEXUS-v0.8.2D / 180 days

Local Role:

- PowerShell and Bash runtime command surfaces.

## Primary PowerShell Entrypoints

```powershell
.\scripts\nexus.ps1 ui
.\scripts\nexus.ps1 tui
.\scripts\nexus.ps1 status
.\scripts\nexus.ps1 evolve
.\scripts\nexus.ps1 reflect
.\scripts\nexus.ps1 domain
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\desktop\open_nexus_gate_console.ps1
```

## Primary Bash Entrypoints

```bash
bash scripts/nexus.sh status
bash scripts/nexus.sh evolve
bash scripts/nexus.sh reflect
bash scripts/nexus.sh domain
bash scripts/nexus.sh electron-env
bash scripts/nexus.sh electron-preflight
```

Validation Surface:

- `python -m unittest discover -s tests`
- `python -m nexus_gate.compiler --root . --json`

Claim Boundary:

- Scripts are governed local surfaces. They do not grant autonomous authority or prove production readiness.
