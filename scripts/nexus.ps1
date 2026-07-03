# NEXUS GATE compact PowerShell command surface
param(
    [ValidateSet("rehydrate", "compile", "once", "loop", "watch", "status", "promote")]
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
    Write-Host "[NG] Failure chart"
    Get-Content .\docs\failure_modes\FAILURE_MODE_CHART.md -TotalCount 80
    Write-Host ""
    Write-Host "[NG] Update chart"
    Get-Content .\docs\updates\UPDATE_CHART.md -TotalCount 80
    Write-Host ""
    if (Test-Path .\reports\nexus_compile_report_latest.json) {
        Write-Host "[NG] Latest compiler report"
        Get-Content .\reports\nexus_compile_report_latest.json -Raw
    }
    if (-not (Test-Path .\reports\nexus_compile_report_latest.json)) {
        Write-Host "[WARN] No latest compiler report found yet."
    }
}

function Run-Loop {
    param([int]$MaxCycles, [int]$SleepSeconds, [switch]$Forever)

    $i = 0
    while ($true) {
        $i += 1
        Write-Host "[NG] Cycle $i"
        Run-Compiler
        if (-not $Forever -and $i -ge $MaxCycles) {
            break
        }
        Start-Sleep -Seconds $SleepSeconds
    }
}

function Show-Status {
    Write-Host "[NG] NEXUS GATE STATUS"
    if (Test-Path .\state\update_index.v0.1.4.json) {
        Write-Host "[NG] Update index"
        Get-Content .\state\update_index.v0.1.4.json -Raw
    }
    if (Test-Path .\state\failure_mode_index.v0.1.4.json) {
        Write-Host "[NG] Failure index"
        Get-Content .\state\failure_mode_index.v0.1.4.json -Raw
    }
    if (Test-Path .\reports\nexus_compile_report_latest.json) {
        Write-Host "[NG] Latest compiler report"
        Get-Content .\reports\nexus_compile_report_latest.json -Raw
    }
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        git status --short
    }
}

function Promote {
    Run-Compiler
    $report = Get-Content .\reports\nexus_compile_report_latest.json -Raw | ConvertFrom-Json
    if ($report.status -ne "pass") {
        throw "Promotion blocked. Compiler status: $($report.status)"
    }

    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd -and -not $NoCommit) {
        git add . | Out-Host
        $status = git status --porcelain
        if ($status) {
            git commit -m "chore: promote NEXUS GATE compact gated pass" | Out-Host
        }
    }

    if ($gitCmd -and $Tag -ne "") {
        git tag $Tag | Out-Host
    }

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
