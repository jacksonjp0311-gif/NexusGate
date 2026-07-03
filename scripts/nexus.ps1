# NEXUS GATE compact PowerShell command surface
param(
    [ValidateSet("rehydrate", "compile", "strict", "pack", "once", "loop", "watch", "status", "promote")]
    [string]$Command = "rehydrate",
    [int]$Cycles = 1,
    [int]$Interval = 5,
    [string]$Tag = "",
    [switch]$NoCommit
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Run-Compiler {
    python -m nexus_gate.compiler --root . --json
    if ($LASTEXITCODE -ne 0) {
        throw "NEXUS GATE compiler failed."
    }
}

function Show-Rehydration {
    Write-Host "[NG] Rehydration visibility"
    Get-Content .\docs\failure_modes\FAILURE_MODE_CHART.md -TotalCount 80
    Write-Host ""
    Get-Content .\docs\updates\UPDATE_CHART.md -TotalCount 80
    Write-Host ""
    if (Test-Path .\docs\goal\GOAL_LOCK.md) {
        Get-Content .\docs\goal\GOAL_LOCK.md -TotalCount 80
    }
    Write-Host ""
    if (Test-Path .\docs\evidence\COLD_EVIDENCE_ENGINE.md) {
        Get-Content .\docs\evidence\COLD_EVIDENCE_ENGINE.md -TotalCount 80
    }
    Write-Host ""
    if (Test-Path .\reports\nexus_compile_report_latest.json) {
        Get-Content .\reports\nexus_compile_report_latest.json -Raw
    }
}

function Run-Loop {
    param([int]$MaxCycles, [int]$SleepSeconds, [switch]$Forever)
    $i = 0
    while ($true) {
        $i += 1
        Write-Host "[NG] Cycle $i"
        Run-Compiler
        if (-not $Forever -and $i -ge $MaxCycles) { break }
        Start-Sleep -Seconds $SleepSeconds
    }
}

function Show-Status {
    Write-Host "[NG] NEXUS GATE STATUS"
    if (Test-Path .\state\goal_lock.v0.1.6.json) { Get-Content .\state\goal_lock.v0.1.6.json -Raw }
    if (Test-Path .\state\pack_index.v0.1.6.json) { Get-Content .\state\pack_index.v0.1.6.json -Raw }
    if (Test-Path .\state\cold_evidence_index.v0.1.5.json) { Get-Content .\state\cold_evidence_index.v0.1.5.json -Raw }
    if (Test-Path .\reports\nexus_compile_report_latest.json) { Get-Content .\reports\nexus_compile_report_latest.json -Raw }
    if (Test-Path .\dist\nexus_gate_pack_manifest_latest.json) { Get-Content .\dist\nexus_gate_pack_manifest_latest.json -Raw }
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) { git status --short }
}

function Promote {
    Run-Compiler
    python -m nexus_gate.build.packer --root . --out dist --json
    if ($LASTEXITCODE -ne 0) { throw "Pack failed. Promotion blocked." }
    $report = Get-Content .\reports\nexus_compile_report_latest.json -Raw | ConvertFrom-Json
    if ($report.status -ne "pass") { throw "Promotion blocked. Compiler status: $($report.status)" }
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd -and -not $NoCommit) {
        git add . | Out-Host
        $status = git status --porcelain
        if ($status) { git commit -m "chore: promote NEXUS GATE packed gated pass" | Out-Host }
    }
    if ($gitCmd -and $Tag -ne "") { git tag $Tag | Out-Host }
    Write-Host "[OK] Promotion gate passed."
}

switch ($Command) {
    "rehydrate" {
        Show-Rehydration
        Run-Compiler
        Write-Host "[OK] Rehydration complete."
    }
    "compile" {
        Run-Compiler
        Write-Host "[OK] Compile passed."
    }
    "strict" {
        powershell -ExecutionPolicy Bypass -File .\scripts\nexus_strict_compile.ps1
    }
    "pack" {
        powershell -ExecutionPolicy Bypass -File .\scripts\nexus_pack.ps1
    }
    "once" {
        Run-Compiler
        Write-Host "[OK] Once passed."
    }
    "loop" {
        Run-Loop -MaxCycles $Cycles -SleepSeconds $Interval
    }
    "watch" {
        Run-Loop -MaxCycles 1 -SleepSeconds $Interval -Forever
    }
    "status" {
        Show-Status
    }
    "promote" {
        Promote
    }
}
