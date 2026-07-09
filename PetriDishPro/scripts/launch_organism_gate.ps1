param(
  [switch]$Install,
  [switch]$NoInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "[Organism Gate] Repo: $Root" -ForegroundColor Cyan

$PkgPath = Join-Path $Root "package.json"
if (Test-Path -LiteralPath $PkgPath) {
  $Pkg = Get-Content -LiteralPath $PkgPath -Raw | ConvertFrom-Json
  $Scripts = @()
  if ($Pkg.scripts) { $Scripts = $Pkg.scripts.PSObject.Properties.Name }

  $Npm = Get-Command npm -ErrorAction SilentlyContinue
  if (-not $Npm) {
    throw "npm was not found. Install Node.js, then rerun this launcher."
  }

  if ($Install -and -not $NoInstall) {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
  }

  if ($Scripts -contains "start") {
    npm start
    exit $LASTEXITCODE
  }

  foreach ($Candidate in @("electron", "dev", "app", "launch")) {
    if ($Scripts -contains $Candidate) {
      npm run $Candidate
      exit $LASTEXITCODE
    }
  }

  throw "package.json exists, but no start/electron/dev/app/launch script was found."
}

$RootLaunchers = Get-ChildItem -Path $Root -File | Where-Object { $_.Name -match '(launch|organism|gate|start|run).*\.(cmd|bat|ps1)$' -and $_.FullName -ne $PSCommandPath }
if ($RootLaunchers.Count -gt 0) {
  $Launcher = $RootLaunchers | Select-Object -First 1
  Write-Host "[Organism Gate] launching $($Launcher.Name)" -ForegroundColor Green
  if ($Launcher.Extension -eq ".ps1") {
    powershell -NoProfile -ExecutionPolicy Bypass -File $Launcher.FullName
    exit $LASTEXITCODE
  }
  & $Launcher.FullName
  exit $LASTEXITCODE
}

throw "No package.json or root launcher was found. See docs/ENTRYPOINT.md."
