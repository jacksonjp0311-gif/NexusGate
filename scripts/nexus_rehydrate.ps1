# NEXUS GATE rehydration visibility script
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "[NG] NEXUS GATE REHYDRATION BOOT"
Write-Host "[NG] Required read order:"
Write-Host "  1. README.md"
Write-Host "  2. docs/context/REHYDRATION_BOOT.md"
Write-Host "  3. docs/context/rehydration_manifest.v0.1.4.json"
Write-Host "  4. docs/failure_modes/FAILURE_MODE_CHART.md"
Write-Host "  5. docs/updates/UPDATE_CHART.md"
Write-Host "  6. state/failure_mode_index.v0.1.4.json"
Write-Host "  7. state/update_index.v0.1.4.json"
Write-Host "  8. reports/nexus_compile_report_latest.json, if present"
Write-Host "  9. rcc/nexus/route_map.json"
Write-Host "  10. target folder README.md"

Write-Host ""
Write-Host "[NG] Failure chart:"
Get-Content .\docs\failure_modes\FAILURE_MODE_CHART.md -TotalCount 80

Write-Host ""
Write-Host "[NG] Update chart:"
Get-Content .\docs\updates\UPDATE_CHART.md -TotalCount 80

Write-Host ""
if (Test-Path .\reports\nexus_compile_report_latest.json) {
    Write-Host "[NG] Latest compiler report:"
    Get-Content .\reports\nexus_compile_report_latest.json -Raw
}
if (-not (Test-Path .\reports\nexus_compile_report_latest.json)) {
    Write-Host "[WARN] No latest compiler report found yet."
}

Write-Host ""
Write-Host "[NG] Running gated compiler after rehydration visibility..."
python -m nexus_gate.compiler --root . --json
if ($LASTEXITCODE -ne 0) {
    throw "Rehydration compiler gate failed."
}
Write-Host "[OK] Rehydration boot complete."
