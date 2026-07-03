# NEXUS GATE v0.3.6 Electron HUD Runtime

The Electron surface is now installed and runnable as a governed local desktop HUD.

## Commands

```powershell
cd electron
npm install
npm start
npm run smoke
```

The app title and visible HUD brand are:

```text
NEXUS GATE
```

## Smoke Report

```text
reports/nexus_electron_smoke_report_latest.json
```

Smoke mode launches Electron hidden, loads the renderer, writes the report, and exits. It does not click lane buttons or run NEXUS lanes.

## Authority Boundary

Electron remains a presentation/operator surface. It may read allowlisted evidence surfaces and request allowlisted NEXUS lanes through `scripts/nexus.ps1`. It may not execute arbitrary shell commands, mutate graph state, bypass evolve, self-authorize, access secrets, write external APIs, or promote memory.
