# NEXUS GATE status
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "🜂 NEXUS GATE STATUS"
Write-Host "Root: $Root"

$statePath = Join-Path $Root "state\nexus_gate_state.v0.1.0.json"
if (Test-Path -LiteralPath $statePath) {
    Write-Host ""
    Write-Host "State:"
    Get-Content $statePath -Raw
}

$reportPath = Join-Path $Root "reports\nexus_compile_report_latest.json"
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content $reportPath -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "Latest compile:"
    Write-Host "  status: $($report.status)"
    Write-Host "  version: $($report.version)"
    Write-Host "  generated: $($report.generated_at_utc)"
    Write-Host "  duration_ms: $($report.duration_ms)"
    Write-Host "  failed gates:"
    $failed = @($report.gates | Where-Object { $_.status -eq "fail" })
    if ($failed.Count -eq 0) {
        Write-Host "    none"
    }
    foreach ($gate in $failed) {
        Write-Host "    $($gate.gate): $($gate.message)"
    }
}

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    Write-Host ""
    Write-Host "Git:"
    git status --short
    git log --oneline -5
}