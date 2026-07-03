# Gated Runtime Loop

The gated runtime loop repeatedly invokes the NEXUS GATE compiler.

## Absolute Rule

```text
Every new runtime loop must exist in both PowerShell and Bash.
Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.
No compile pass, no promotion.
```

## PowerShell Commands

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 5 -IntervalSeconds 5
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_watch.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_status.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_promote.ps1
```

## Bash Commands

```bash
bash scripts/nexus_once.sh
bash scripts/nexus_dev_loop.sh --max-cycles 5 --interval 5
bash scripts/nexus_watch.sh
bash scripts/nexus_status.sh
bash scripts/nexus_promote.sh
```

## Loop Behavior

```text
start cycle
  -> run compiler
  -> read latest report
  -> display pass/fail
  -> append loop log
  -> optionally commit clean pass
  -> stop or sleep
next cycle
```

## Failure Rule

```text
Failure never promotes.
Failure never auto-commits.
Failure writes a report.
Failure can stop the loop when StopOnFail / --stop-on-fail is set.
```