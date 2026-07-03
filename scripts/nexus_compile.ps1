# NEXUS GATE gated compile wrapper
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "🜂 NEXUS GATE gated compile starting..."
python -m nexus_gate.compiler --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE gated compile failed with exit code $LASTEXITCODE"
}
Write-Host "✓ NEXUS GATE gated compile passed."