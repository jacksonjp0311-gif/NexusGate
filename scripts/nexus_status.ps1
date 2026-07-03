$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "🜂 NEXUS GATE STATUS"
if (Test-Path .\state\nexus_gate_state.v0.1.3.json) { Get-Content .\state\nexus_gate_state.v0.1.3.json -Raw }
if (Test-Path .\reports\nexus_compile_report_latest.json) { Get-Content .\reports\nexus_compile_report_latest.json -Raw }
git status --short
