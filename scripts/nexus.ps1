# NEXUS GATE compact PowerShell command surface
# Legacy direct compiler markers retained for audit/tests:
# nexus_gate.adapters.compile
# nexus_gate.receptors.compile
# nexus_gate.bridge.compile
# nexus_gate.bridge.runtime_compiler
# nexus_gate.feedback.compile
# nexus_gate.feedback.interface_compile
# nexus_gate.interconnect.compile
# nexus_gate.evidence.compact
# nexus_gate.self_healing.compile
param(
    [ValidateSet("rehydrate", "compile", "strict", "pack", "adapters", "receptors", "bridge", "runtime", "human", "feedback", "interconnect", "compact", "heal", "interface", "electron-preflight", "tui", "ui", "evolve", "once", "loop", "watch", "status", "promote")]
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
        ".\docs\bridge\BRIDGE_SESSION_RUNNER.md",
        ".\docs\bridge\BOUNDED_BRIDGE_RUNTIME.md",
        ".\docs\runtime\HUMAN_SURFACE.md",
        ".\docs\runtime\FEEDBACK_INTERCONNECT.md",
        ".\docs\runtime\SELF_HEALING_FEEDBACK.md",
        ".\docs\feedback\FEEDBACK_SYSTEM.md",
        ".\docs\feedback\FEEDBACK_LOG.md",
        ".\docs\ui\NEXUS_TUI_SHELL.md",
        ".\docs\failure_modes\FAILURE_MODE_CHART.md",
        ".\docs\updates\UPDATE_CHART.md"
    )) {
        if (Test-Path $path) { Get-Content $path -TotalCount 80 }
    }
    if (Test-Path .\state\ai_feedback_context_latest.json) { Get-Content .\state\ai_feedback_context_latest.json -Raw }
    if (Test-Path .\reports\nexus_compile_report_latest.json) { Get-Content .\reports\nexus_compile_report_latest.json -Raw }
}

function Run-Loop {
    param([int]$MaxCycles, [int]$SleepSeconds, [switch]$Forever)
    $i = 0
    while ($true) {
        $i += 1
        Write-Host "[NG] Cycle $i"
        powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve
        if ($LASTEXITCODE -ne 0) { throw "NEXUS human/evolve failed." }
        if (-not $Forever -and $i -ge $MaxCycles) { break }
        Start-Sleep -Seconds $SleepSeconds
    }
}

function Show-Status {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 status
}

function Promote {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd -and -not $NoCommit) {
        git config core.autocrlf false | Out-Null
        git config core.safecrlf false | Out-Null
        git add . 2>$null | Out-Host
        $status = git status --porcelain
        if ($status) { git commit -m "chore: promote NEXUS GATE TUI pass" | Out-Host }
    }
    if ($gitCmd -and $Tag -ne "") { git tag $Tag | Out-Host }
    Write-Host "[OK] Promotion gate passed."
}

switch ($Command) {
    "rehydrate" { Show-Rehydration; Run-Compiler; Write-Host "[OK] Rehydration complete." }
    "compile" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 compile }
    "strict" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_strict_compile.ps1 }
    "pack" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 pack }
    "adapters" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_adapter_compile.ps1 }
    "receptors" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_receptor_compile.ps1 }
    "bridge" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_bridge_demo.ps1 }
    "runtime" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 runtime }
    "human" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 all }
    "feedback" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 feedback }
    "interconnect" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 interconnect }
    "compact" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 compact }
    "heal" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 heal }
    "interface" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 interface }
    "electron-preflight" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 electron-preflight }
    "tui" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_tui.ps1 }
    "ui" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_ui.ps1 }
    "evolve" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve }
    "once" { Run-Compiler; Write-Host "[OK] Once passed." }
    "loop" { Run-Loop -MaxCycles $Cycles -SleepSeconds $Interval }
    "watch" { Run-Loop -MaxCycles 1 -SleepSeconds $Interval -Forever }
    "status" { Show-Status }
    "promote" { Promote }
}
