# NEXUS GATE pack compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m nexus_gate.build.packer --root . --out dist --json
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS GATE pack failed."
}
Write-Host "[OK] NEXUS GATE pack complete."
