# NEXUS GATE bounded runtime compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m nexus_gate.bridge.runtime_compiler --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE runtime compile failed."
}
Write-Host "[OK] NEXUS GATE bounded runtime compile complete."
