# NEXUS GATE v0.3.3 Electron Shell Scaffold

The repository now includes a minimal Electron operator shell scaffold under:

```text
electron/
```

The scaffold is intentionally thin. It reads declared evidence surfaces, renders operator state, and can request only allowlisted NEXUS lanes through `scripts/nexus.ps1`.

## Runtime Boundary

```text
Electron renderer
  -> preload bridge
  -> main process IPC
  -> allowlisted read surface or NEXUS lane
  -> existing NEXUS evidence/gates
```

## Guardrails

```text
contextIsolation: true
nodeIntegration: false
sandbox: true
spawn shell: false
no exec
no arbitrary command input
no graph mutation
no secret access
no external API writes
```

## Status

This surface now has a local installed Electron runtime and committed lockfile. It is still not packaged or production validated. It does not replace the PowerShell TUI, and it does not own NEXUS logic.
