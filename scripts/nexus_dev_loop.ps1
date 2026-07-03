# NEXUS GATE Gated Dev Loop — PowerShell
param(
    [int]$MaxCycles = 1,
    [int]$IntervalSeconds = 5,
    [switch]$Watch,
    [switch]$AutoCommit,
    [switch]$StopOnFail
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Run-Compiler {
    python -m nexus_gate.compiler --root . --json
    return $LASTEXITCODE
}

$cycle = 0
while ($true) {
    $cycle += 1
    Write-Host "🜂 NEXUS GATE cycle $cycle"
    $code = Run-Compiler
    if ($code -ne 0) {
        Write-Host "⚠ Cycle failed. No promotion."
        if ($StopOnFail) { exit $code }
    } else {
        Write-Host "✓ Cycle passed."
        if ($AutoCommit) {
            git add .
            if (git status --porcelain) {
                git commit -m "chore: gated dev loop pass"
            }
        }
    }
    if (-not $Watch -and $cycle -ge $MaxCycles) { break }
    Start-Sleep -Seconds $IntervalSeconds
}
