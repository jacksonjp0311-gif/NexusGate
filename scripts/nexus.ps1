# NEXUS GATE compact PowerShell command surface
param(
    [ValidateSet("rehydrate", "compile", "strict", "pack", "adapters", "receptors", "once", "loop", "watch", "status", "promote")]
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
    if ($LASTEXITCODE -ne 0) { throw "NEXUS GATE compiler failed." }
}

function Show-Rehydration {
    Write-Host "[NG] Rehydration visibility"
    foreach ($path in @(
        ".\docs\goal\GOAL_LOCK.md",
        ".\docs\adapters\ADAPTER_REGISTRY.md",
        ".\docs\receptors\RECEPTOR_REGISTRY.md",
        ".\docs\failure_modes\FAILURE_MODE_CHART.md",
        ".\docs\updates\UPDATE_CHART.md"
    )) {
        if (Test-Path $path) { Get-Content $path -TotalCount 80 }
    }
    if (Test-Path .\reports\nexus_compile_report_latest.json) { Get-Content .\reports\nexus_compile_report_latest.json -Raw }
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
    foreach ($path in @(
        ".\state\goal_lock.v0.1.6.json",
        ".\state\adapter_registry_index.v0.1.7.json",
        ".\state\receptor_registry_index.v0.1.8.json",
        ".\state\pack_index.v0.1.6.json",
        ".\reports\nexus_receptor_compile_report_latest.json",
        ".\reports\nexus_adapter_compile_report_latest.json",
        ".\reports\nexus_compile_report_latest.json",
        ".\dist\nexus_gate_pack_manifest_latest.json"
    )) { if (Test-Path $path) { Get-Content $path -Raw } }
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) { git status --short }
}

function Promote {
    Run-Compiler
    python -m nexus_gate.adapters.compile --root . --json
    if ($LASTEXITCODE -ne 0) { throw "Adapter compile failed. Promotion blocked." }
    python -m nexus_gate.receptors.compile --root . --json
    if ($LASTEXITCODE -ne 0) { throw "Receptor compile failed. Promotion blocked." }
    python -m nexus_gate.build.packer --root . --out dist --json
    if ($LASTEXITCODE -ne 0) { throw "Pack failed. Promotion blocked." }
    $report = Get-Content .\reports\nexus_compile_report_latest.json -Raw | ConvertFrom-Json
    if ($report.status -ne "pass") { throw "Promotion blocked. Compiler status: $($report.status)" }
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd -and -not $NoCommit) {
        git add . | Out-Host
        $status = git status --porcelain
        if ($status) { git commit -m "chore: promote NEXUS GATE adapter receptor packed pass" | Out-Host }
    }
    if ($gitCmd -and $Tag -ne "") { git tag $Tag | Out-Host }
    Write-Host "[OK] Promotion gate passed."
}

switch ($Command) {
    "rehydrate" { Show-Rehydration; Run-Compiler; Write-Host "[OK] Rehydration complete." }
    "compile" { Run-Compiler; Write-Host "[OK] Compile passed." }
    "strict" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_strict_compile.ps1 }
    "pack" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_pack.ps1 }
    "adapters" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_adapter_compile.ps1 }
    "receptors" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_receptor_compile.ps1 }
    "once" { Run-Compiler; Write-Host "[OK] Once passed." }
    "loop" { Run-Loop -MaxCycles $Cycles -SleepSeconds $Interval }
    "watch" { Run-Loop -MaxCycles 1 -SleepSeconds $Interval -Forever }
    "status" { Show-Status }
    "promote" { Promote }
}
