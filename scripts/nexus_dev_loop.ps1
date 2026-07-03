# NEXUS GATE Gated Dev Loop — PowerShell
param(
    [int]$MaxCycles = 1,
    [int]$IntervalSeconds = 5,
    [switch]$Watch,
    [switch]$AutoCommit,
    [switch]$StopOnFail,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Say {
    param([string]$Message, [string]$Glyph = "🜂")
    Write-Host "$Glyph $Message"
}

function Append-Log {
    param([string]$Message)
    $logDir = Join-Path $Root "logs"
    if (-not (Test-Path -LiteralPath $logDir)) {
        [void](New-Item -ItemType Directory -Path $logDir -Force)
    }
    $line = "$(Get-Date -Format o) $Message"
    Add-Content -Path (Join-Path $logDir "nexus_dev_loop.log") -Value $line -Encoding utf8
}

function Get-LatestReport {
    $path = Join-Path $Root "reports\nexus_compile_report_latest.json"
    if (Test-Path -LiteralPath $path) {
        return Get-Content $path -Raw | ConvertFrom-Json
    }
    return $null
}

function Run-Compiler {
    $consolePath = Join-Path $Root "logs\nexus_compile_console_latest.log"
    Say "Running gated compiler." "🜂"
    Append-Log "compile_start shell=powershell"

    & python -m nexus_gate.compiler --root . --json 2>&1 | Tee-Object -FilePath $consolePath
    $code = $LASTEXITCODE

    $report = Get-LatestReport

    if ($null -eq $report) {
        Append-Log "compile_no_report shell=powershell exit_code=$code"
        throw "Compiler did not write reports\nexus_compile_report_latest.json"
    }

    if ($code -ne 0) {
        Append-Log "compile_fail shell=powershell exit_code=$code status=$($report.status)"
        return @{
            ok = $false
            code = $code
            report = $report
        }
    }

    Append-Log "compile_pass shell=powershell duration_ms=$($report.duration_ms)"
    return @{
        ok = $true
        code = 0
        report = $report
    }
}

function Commit-CleanPass {
    param([object]$Report)

    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCmd) {
        Say "Git not found. Skipping auto-commit." "∿"
        return
    }

    git add . | Out-Host
    $status = git status --porcelain

    if (-not $status) {
        Say "No changes to commit." "✓"
        return
    }

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    git commit -m "chore: gated dev loop pass $stamp" | Out-Host
    Append-Log "auto_commit shell=powershell pass duration_ms=$($Report.duration_ms)"
}

$cycle = 0

while ($true) {
    $cycle += 1
    Say "NEXUS GATE cycle $cycle started." "🜂"
    Append-Log "cycle_start shell=powershell cycle=$cycle"

    $result = Run-Compiler
    $report = $result.report

    if ($result.ok) {
        Say "Cycle $cycle PASS. Duration: $($report.duration_ms) ms" "✓"

        if ($AutoCommit) {
            Commit-CleanPass -Report $report
        }
    }

    if (-not $result.ok) {
        Say "Cycle $cycle FAIL. Report: reports\nexus_compile_report_latest.json" "⚠"
        if ($StopOnFail) {
            Append-Log "cycle_stop_on_fail shell=powershell cycle=$cycle"
            break
        }
    }

    if ($OpenReport) {
        Start-Process (Join-Path $Root "reports\nexus_compile_report_latest.json")
    }

    Append-Log "cycle_end shell=powershell cycle=$cycle status=$($report.status)"

    if (-not $Watch) {
        if ($cycle -ge $MaxCycles) {
            break
        }
    }

    Say "Sleeping $IntervalSeconds seconds." "∿"
    Start-Sleep -Seconds $IntervalSeconds
}

Say "NEXUS GATE dev loop complete." "🜂"