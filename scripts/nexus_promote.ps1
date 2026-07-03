# NEXUS GATE promotion gate
param(
    [string]$Tag = "",
    [switch]$NoCommit
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Say {
    param([string]$Message, [string]$Glyph = "🜂")
    Write-Host "$Glyph $Message"
}

Say "Running promotion gate." "🜂"

powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1

$reportPath = Join-Path $Root "reports\nexus_compile_report_latest.json"
if (-not (Test-Path -LiteralPath $reportPath)) {
    throw "Latest compile report missing."
}

$report = Get-Content $reportPath -Raw | ConvertFrom-Json
if ($report.status -ne "pass") {
    throw "Promotion blocked. Compiler status: $($report.status)"
}

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Say "Git not found. Promotion gate passed without Git checkpoint." "∿"
    exit 0
}

if (-not $NoCommit) {
    git add . | Out-Host
    $status = git status --porcelain
    if ($status) {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        git commit -m "chore: promote NEXUS GATE gated pass $stamp" | Out-Host
    }
}

if ($Tag -ne "") {
    git tag $Tag | Out-Host
    Say "Tag created: $Tag" "✓"
}

Say "Promotion gate passed." "✓"