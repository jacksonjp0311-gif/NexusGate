# Gated Runtime Loop

Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 5
```

Bash:

```bash
bash scripts/nexus_dev_loop.sh --max-cycles 5
```
