$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm was not found. Install Node.js LTS, then run this again." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".\node_modules")) {
    npm install
}

npm start
