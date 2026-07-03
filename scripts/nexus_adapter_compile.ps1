# NEXUS GATE adapter compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m nexus_gate.adapters.compile --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE adapter compile failed."
}
Write-Host "[OK] NEXUS GATE adapter compile complete."
