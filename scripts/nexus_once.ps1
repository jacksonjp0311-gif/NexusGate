# Run NEXUS GATE gated compiler once.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 1 -StopOnFail