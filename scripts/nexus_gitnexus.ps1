# NEXUS GITNEXUS operator lane
# Evidence-only. No autonomous authority.

param(
    [ValidateSet('scan', 'status', 'open')]
    [string]$Command = 'scan'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($Command -eq 'scan') {
    python -m nexus_gate.gitnexus_bridge --root . --json
    if ($LASTEXITCODE -ne 0) { throw 'GITNEXUS scan failed.' }
}

if ($Command -eq 'status') {
    if (Test-Path '.\reports\gitnexus_report_latest.json') {
        Get-Content '.\reports\gitnexus_report_latest.json' -Raw
    }
    if (-not (Test-Path '.\reports\gitnexus_report_latest.json')) {
        Write-Host 'No GITNEXUS report found. Run .\scripts\nexus_gitnexus.ps1 scan'
    }
}

if ($Command -eq 'open') {
    Start-Process (Resolve-Path '.\GITNEXUS\hud\index.html')
}
