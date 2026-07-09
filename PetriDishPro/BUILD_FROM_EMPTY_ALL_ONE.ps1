# PETRI DISH PRO — EMPTY FOLDER BOOTSTRAP NOTE
# This zip is already built. Use RUN_DEMO_ALL_ONE.ps1 from the repo root.
# This file exists as a stable anchor for future NexusGate-style All-One expansion.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
Write-Host "Petri Dish Pro already contains the generated source tree." -ForegroundColor Cyan
Write-Host "Run: .\RUN_DEMO_ALL_ONE.ps1" -ForegroundColor Green
