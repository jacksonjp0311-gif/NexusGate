# NEXUS GATE local checks
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Running Python compile check..."
python -m compileall nexus_gate tests

Write-Host "Running unit tests..."
python -m unittest discover -s tests

Write-Host "Demo route..."
python -m nexus_gate.cli route examples\packet.demo.shadow.json