$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 interconnect
