# Cross-Platform Commands

NEXUS GATE maintains paired PowerShell and Bash surfaces.

## Compile

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_compile.ps1
```

Bash:

```bash
bash scripts/nexus_compile.sh
```

## Run Once

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

Bash:

```bash
bash scripts/nexus_once.sh
```

## Dev Loop

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 5
```

Bash:

```bash
bash scripts/nexus_dev_loop.sh --max-cycles 5
```

## Watch

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_watch.ps1
```

Bash:

```bash
bash scripts/nexus_watch.sh
```

## Status

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_status.ps1
```

Bash:

```bash
bash scripts/nexus_status.sh
```

## Promote

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_promote.ps1
```

Bash:

```bash
bash scripts/nexus_promote.sh
```