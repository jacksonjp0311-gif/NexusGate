# NEXUS GATE Electron HUD

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): ui, runtime, evidence, operator
- Sector: electron
- Version / TTL: NG-RHP-NEXUS-v0.8.2D / 180 days

Local Role:

- Local Electron operator HUD for NEXUS evidence, chat, Mode Selection, telemetry, HANDOFF packets, and governed lane requests.

## Run

```powershell
cd electron
npm install
npm start
npm run smoke
```

## Boundary

Electron is presentation/operator surface only. It may read declared evidence surfaces, request allowlisted NEXUS lanes, and render operator state. It may not execute arbitrary shell commands, mutate graph state, self-authorize, access secrets, write external APIs, bypass evolve, or prove validation.
