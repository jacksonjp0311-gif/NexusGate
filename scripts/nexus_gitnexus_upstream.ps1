# scripts/nexus_gitnexus_upstream.ps1
# Helper for real GitNexus upstream bridge.
#
# Usage:
#   .\scripts\nexus_gitnexus_upstream.ps1 analyze
#   .\scripts\nexus_gitnexus_upstream.ps1 serve
#   .\scripts\nexus_gitnexus_upstream.ps1 full
#   .\scripts\nexus_gitnexus_upstream.ps1 status

param(
    [ValidateSet("analyze", "serve", "full", "status", "doctor")]
    [string]$Mode = "serve"
)

$ErrorActionPreference = "Stop"

function Say([string]$Message, [string]$Glyph = "[GNX]") {
    Write-Host ($Glyph + " " + $Message)
}

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Say ("Root anchored: " + $Root)

function Invoke-GitNexus([string[]]$Args) {
    $cmd = Get-Command gitnexus -ErrorAction SilentlyContinue
    if ($cmd) {
        & gitnexus @Args
        exit $LASTEXITCODE
    }

    $npx = Get-Command npx -ErrorAction SilentlyContinue
    if ($npx) {
        & npx -y gitnexus@latest @Args
        exit $LASTEXITCODE
    }

    throw "gitnexus/npx not found. Install Node.js, then run: npm install -g gitnexus"
}

if ($Mode -eq "analyze") {
    Say "Running GitNexus analyze against this repo."
    Invoke-GitNexus @("analyze", ".", "--force", "--skip-skills")
}

if ($Mode -eq "full") {
    Say "Running GitNexus full analyze against this repo."
    Invoke-GitNexus @("analyze", ".", "--force", "--embeddings", "--skip-skills")
}

if ($Mode -eq "serve") {
    Say "Starting GitNexus local bridge server. Keep this terminal open."
    Say "Then open NexusGate UI and click GITNEXUS -> OPEN."
    Invoke-GitNexus @("serve")
}

if ($Mode -eq "status") {
    Invoke-GitNexus @("status")
}

if ($Mode -eq "doctor") {
    Invoke-GitNexus @("doctor")
}