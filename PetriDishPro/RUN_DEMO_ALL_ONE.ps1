param([string]$Preset="microbial_competition",[int]$Steps=80,[int]$Grid=56)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Repo
Write-Host "[PETRI] compileall" -ForegroundColor Cyan
& python -m compileall petri_lab tests
if ($LASTEXITCODE -ne 0) { throw "compileall failed with exit code $LASTEXITCODE" }
Write-Host "[PETRI] unittest" -ForegroundColor Cyan
& python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw "unittest failed with exit code $LASTEXITCODE" }
Write-Host "[PETRI] run preset $Preset" -ForegroundColor Cyan
& python -m petri_lab.cli --root . --preset $Preset --steps $Steps --grid $Grid --json
if ($LASTEXITCODE -ne 0) { throw "simulation failed with exit code $LASTEXITCODE" }
Write-Host "[PETRI] sealed. Latest receipt: reports\bio\petri_run_latest.json" -ForegroundColor Green
