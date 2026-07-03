# NEXUS GATE receptor compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m nexus_gate.receptors.compile --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE receptor compile failed."
}
Write-Host "[OK] NEXUS GATE receptor compile complete."
