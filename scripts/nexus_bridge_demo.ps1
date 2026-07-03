# NEXUS GATE bridge demo compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m nexus_gate.bridge.compile --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE bridge compile failed."
}
Write-Host "[OK] NEXUS GATE bridge compile complete."
