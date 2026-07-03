# NEXUS GATE v0.3.5 Electron Environment Gate

This gate checks whether the local machine is ready for a future governed Electron smoke test.

## Command

```powershell
.\scripts\nexus.ps1 electron-env
```

Bash:

```bash
bash scripts/nexus.sh electron-env
```

## Report

```text
reports/nexus_electron_environment_report_latest.json
```

## Checks

```text
electron/package.json exists
Electron dependency is declared
node is available
npm is available
electron/node_modules/electron is present
```

Missing Node, npm, or installed Electron dependencies are warnings, not repo failures. The report can say the environment is `not_ready` while the gate still passes, because this compiler does not install dependencies or mutate the desktop scaffold.

As of v0.3.6, local Electron dependencies have been installed on the operator machine and `electron/package-lock.json` is committed for reproducible installs. `electron/node_modules/` remains ignored and must be recreated with `npm install` after clone.

## Boundary

The environment gate does not install dependencies, launch Electron, package an EXE, run arbitrary shell commands, write external APIs, read secrets, or grant autonomous authority.
