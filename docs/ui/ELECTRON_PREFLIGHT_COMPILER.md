# NEXUS GATE v0.3.4 Electron Preflight Compiler

The Electron scaffold now has a preflight compiler.

## Command

```powershell
.\scripts\nexus.ps1 electron-preflight
```

Bash:

```bash
bash scripts/nexus.sh electron-preflight
```

## Report

```text
reports/nexus_electron_preflight_report_latest.json
```

## Checks

```text
required scaffold paths
read contract allowlist
blocked actions
snapshot/surface pair
main-process security markers
preload API boundary
renderer preload bridge usage
private package scaffold
claim boundary
```

## Boundary

This compiler does not install, package, launch, or validate Electron. It only verifies the local scaffold contract before future desktop promotion.
