param(
    [string]$Source = "$env:USERPROFILE\OneDrive\Desktop\Cortex",
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$sourcePath = Resolve-Path -LiteralPath $Source
$targetPath = Join-Path $Root "Cortex"
$reportsPath = Join-Path $Root "reports"
New-Item -ItemType Directory -Force -Path $targetPath, $reportsPath | Out-Null

$excludeDirs = @(
    ".git",
    ".cortex",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "work",
    "cortex_memory.egg-info"
)
$excludeFiles = @("*.pyc", "*.pyo", ".coverage")

$args = @(
    $sourcePath.Path,
    $targetPath,
    "/E",
    "/XD"
) + $excludeDirs + @("/XF") + $excludeFiles + @("/NFL", "/NDL", "/NJH", "/NJS", "/NP")

& robocopy @args | Out-Null
$code = $LASTEXITCODE
if ($code -gt 7) {
    throw "Cortex sync failed with robocopy exit code $code."
}

$sourceCommit = $null
try {
    $sourceCommit = (& git -C $sourcePath.Path rev-parse --short HEAD).Trim()
} catch {
    $sourceCommit = "unknown"
}

$report = [ordered]@{
    system = "NEXUS GATE"
    lane = "sync-cortex"
    status = "pass"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source = $sourcePath.Path
    target = $targetPath
    source_commit = $sourceCommit
    copied_surface = "Cortex source/docs/tests/benchmarks only"
    excluded_dirs = $excludeDirs
    excluded_files = $excludeFiles
    authority_boundary = "Cortex sync copies local source artifacts only. It does not import upstream git history, runtime memory, secrets, caches, external APIs, or grant Cortex mutation authority."
    next_action = ".\scripts\nexus.ps1 cortex"
}

$latest = Join-Path $reportsPath "nexus_cortex_sync_report_latest.json"
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $latest

$versioned = Join-Path $reportsPath ("nexus_cortex_sync_report_{0}.json" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $versioned

$report | ConvertTo-Json -Depth 5
