# NEXUS GATE v0.3.5 TUI HUD Operator Surface

The PowerShell TUI and Electron scaffold now share the same HUD visual direction:

```text
top status strip
process lane panel
central NEXUS console
feedback summary panel
AI handoff package panel
lower human/AI/debug/self-healing/reflection/interconnect modules
governance footer
```

The TUI remains the canonical proof surface:

```powershell
.\scripts\nexus.ps1 tui
```

Compatibility alias:

```powershell
.\scripts\nexus.ps1 ui
```

The HUD snapshot command writes:

```text
reports/tui/nexus_tui_snapshot_latest.html
reports/tui/nexus_tui_surface_latest.json
```

## Boundary

The HUD is presentation only. It may show governed lanes, evidence state, feedback summaries, and export surfaces. It does not own logic, self-authorize, bypass compiler/evolve gates, mutate graph state, install Electron, launch Electron, or package a desktop executable.
