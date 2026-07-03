# Run NEXUS GATE gated compiler continuously.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -Watch -IntervalSeconds 10