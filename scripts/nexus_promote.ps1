param([string]$Tag = "", [switch]$NoCommit)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python -m nexus_gate.compiler --root . --json
if ($LASTEXITCODE -ne 0) { throw "Promotion blocked. Compiler failed." }
if (-not $NoCommit) {
    git add .
    if (git status --porcelain) { git commit -m "chore: promote NEXUS GATE gated pass" }
}
if ($Tag -ne "") { git tag $Tag }
Write-Host "✓ Promotion gate passed."
