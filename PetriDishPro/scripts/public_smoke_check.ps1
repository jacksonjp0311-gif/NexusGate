param(
  [switch]$NoNodeInstall,
  [switch]$NoElectronLaunch,
  [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Find-Root {
  $cursor = Split-Path -Parent $PSCommandPath
  while ($cursor) {
    if (Test-Path -LiteralPath (Join-Path $cursor ".git")) { return $cursor }
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor) { break }
    $cursor = $parent
  }
  return (Resolve-Path ".").Path
}

function Run-Cmd($Name, [scriptblock]$Body) {
  & $Body
  if ($LASTEXITCODE -ne 0) {
    throw "$Name failed with exit code $LASTEXITCODE"
  }
}

$Root = Find-Root
Set-Location $Root

$ReportDir = Join-Path $Root "reports/public"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$Report = [ordered]@{
  system = "PETRI_PUBLIC_SMOKE_CHECK"
  root = $Root
  started_utc = (Get-Date).ToUniversalTime().ToString("o")
  scan_mode = "git-ls-files"
  powershell = "5.1-compatible"
  gates = @()
}

function Add-Gate($Name, $Status, $Evidence) {
  $Report.gates += [ordered]@{
    gate = $Name
    status = $Status
    evidence = $Evidence
    utc = (Get-Date).ToUniversalTime().ToString("o")
  }
}

function Pass($Name, $Evidence=@{}) {
  Write-Host "[PUBLIC SMOKE] $Name PASS" -ForegroundColor Green
  Add-Gate $Name "pass" $Evidence
}

function Fail($Name, $Message) {
  Write-Host "[PUBLIC SMOKE] $Name FAIL: $Message" -ForegroundColor Red
  Add-Gate $Name "fail" @{ error = $Message }
  throw $Message
}

try {
  $Slash = [char]92
  $Forward = [char]47
  $CanonicalRepo = "https://github.com/jacksonjp0311-gif/PetriDishPro.git"
  $UserRootNeedle = ("C:" + $Slash + "Users" + $Slash + "jacks")
  $UserRootNeedleAlt = ("C:" + $Forward + "Users" + $Forward + "jacks")
  $OneDriveNeedle = ("OneDrive" + $Slash + "Desktop" + $Slash + "PetriDishPro")
  $OneDriveNeedleAlt = ("OneDrive" + $Forward + "Desktop" + $Forward + "PetriDishPro")
  $OldRepoNeedle = "github.com/jacksonjp0311-gif/" + "-PetriDishPro"
  $OldCdNeedle = "cd " + "-PetriDishPro"

  if (-not (Test-Path -LiteralPath "README.md")) { Fail "README" "README.md missing" }
  $Readme = Get-Content -LiteralPath "README.md" -Raw
  if ($Readme -notlike "*$CanonicalRepo*") { Fail "README" "canonical clone URL missing" }
  if ($Readme -like "*$UserRootNeedle*" -or $Readme -like "*$UserRootNeedleAlt*" -or $Readme -like "*$OneDriveNeedle*" -or $Readme -like "*$OneDriveNeedleAlt*" -or $Readme -like "*$OldRepoNeedle*" -or $Readme -like "*$OldCdNeedle*") {
    Fail "README" "README contains local path or old repo identity"
  }
  Pass "README" @{ canonical = $true }

  $Docs = @("docs/ENTRYPOINT.md", "docs/TOOL_CAPABILITIES.md", "docs/PROJECT_STRUCTURE.md")
  foreach ($Doc in $Docs) {
    if (-not (Test-Path -LiteralPath $Doc)) { Fail "DOCS" "$Doc missing" }
  }
  Pass "DOCS" @{ docs = $Docs }

  $Svg = "docs/assets/organism-gate-entrypoint.svg"
  if (-not (Test-Path -LiteralPath $Svg)) { Fail "GRAPHIC" "entrypoint svg missing" }
  $SvgText = Get-Content -LiteralPath $Svg -Raw
  if ($SvgText -like "*<circle*") { Fail "GRAPHIC" "entrypoint svg contains removed circle element" }
  if ($SvgText -notlike "*viewBox=`"0 0 1280 420`"*") { Fail "GRAPHIC" "entrypoint svg viewBox not expected public-safe size" }
  Pass "GRAPHIC" @{ svg = $Svg }

  $LeakPatterns = @(
    $UserRootNeedle,
    $UserRootNeedleAlt,
    $OneDriveNeedle,
    $OneDriveNeedleAlt,
    $OldRepoNeedle,
    $OldCdNeedle
  )

  $Tracked = @(git ls-files)
  if ($LASTEXITCODE -ne 0) { Fail "GIT_TRACKED_LIST" "git ls-files failed" }
  $Leaks = @()

  foreach ($Relative in $Tracked) {
    if ($Relative -match '^(reports/public/|reports/bio/|artifacts/bio/runs/|_backup/|\.petri_backups/|backups/|node_modules/|\.venv/|venv/|__pycache__/)' ) { continue }
    if ($Relative -match '\.(png|ico|jpg|jpeg|gif|pdf|zip|exe|dll)$') { continue }
    if (-not (Test-Path -LiteralPath $Relative)) { continue }

    $Text = Get-Content -LiteralPath $Relative -Raw -ErrorAction SilentlyContinue
    if ($null -eq $Text) { continue }

    foreach ($Needle in $LeakPatterns) {
      if ($Text -like "*$Needle*") {
        $Leaks += "$Relative -> $Needle"
        break
      }
    }
  }

  if ($Leaks.Count -gt 0) { Fail "PUBLIC_LEAK_SCAN" ($Leaks -join "; ") }
  Pass "PUBLIC_LEAK_SCAN" @{ tracked_files_scanned = $Tracked.Count }

  Run-Cmd "python compileall" { python -m compileall -q petri_lab tests }
  Pass "PYTHON_COMPILEALL" @{ exit = 0 }

  Run-Cmd "python tests" { python -m unittest discover -s tests }
  Pass "PYTHON_TESTS" @{ exit = 0 }

  $PkgPath = Join-Path $Root "package.json"
  if (Test-Path -LiteralPath $PkgPath) {
    $Pkg = Get-Content -LiteralPath $PkgPath -Raw | ConvertFrom-Json
    $Scripts = @()
    if ($Pkg.scripts) { $Scripts = $Pkg.scripts.PSObject.Properties.Name }
    if ($Scripts.Count -eq 0) { Fail "NODE_PACKAGE" "package.json has no scripts" }
    Pass "NODE_PACKAGE" @{ scripts = $Scripts }

    if (-not $NoNodeInstall) {
      $Npm = Get-Command npm -ErrorAction SilentlyContinue
      if ($Npm) {
        Run-Cmd "npm install" { npm install }
        Pass "NPM_INSTALL" @{ exit = 0 }
      }
      if (-not $Npm) { Pass "NPM_INSTALL" @{ skipped = "npm not found" } }
    }
  }
  else {
    Pass "NODE_PACKAGE" @{ skipped = "package.json not present" }
  }

  $RootLaunchers = Get-ChildItem -Path $Root -File | Where-Object { $_.Name -match '(launch|organism|gate|start|run).*\.(ps1|cmd|bat)$' }
  $ScriptLaunchers = Get-ChildItem -Path (Join-Path $Root "scripts") -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(launch|organism|gate|start|run).*\.(ps1|cmd|bat)$' }
  $LauncherNames = @($RootLaunchers.Name + $ScriptLaunchers.Name) | Where-Object { $_ }
  if ($LauncherNames.Count -eq 0) { Fail "ENTRYPOINT_LAUNCHERS" "no launcher script found" }
  Pass "ENTRYPOINT_LAUNCHERS" @{ launchers = $LauncherNames }

  $Report.status = "passed"
  $Report.finished_utc = (Get-Date).ToUniversalTime().ToString("o")
  $Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ReportDir "public_smoke_check_latest.json") -Encoding UTF8
  Write-Host "[PUBLIC SMOKE] COMPLETE PASS" -ForegroundColor Green
}
catch {
  $Report.status = "failed"
  $Report.finished_utc = (Get-Date).ToUniversalTime().ToString("o")
  $Report.error = $_.Exception.Message
  $Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ReportDir "public_smoke_check_latest.json") -Encoding UTF8
  throw
}
