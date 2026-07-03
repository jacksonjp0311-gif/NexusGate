# NEXUS GATE strict compiler
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "[NG] Strict compile: Python compile"
python -m compileall nexus_gate tests
if ($LASTEXITCODE -ne 0) { throw "Python compile failed." }

Write-Host "[NG] Strict compile: unit tests"
python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw "Unit tests failed." }

Write-Host "[NG] Strict compile: NEXUS compiler"
python -m nexus_gate.compiler --root . --json
if ($LASTEXITCODE -ne 0) { throw "NEXUS compiler failed." }

Write-Host "[NG] Strict compile: compact rehydration"
powershell -ExecutionPolicy Bypass -File .\scripts\nexus.ps1 rehydrate
if ($LASTEXITCODE -ne 0) { throw "Compact rehydration failed." }

Write-Host "[OK] Strict compiler passed."
