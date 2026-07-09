
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-GateLine {
    param([string]$Text = "", [string]$Color = "Gray")
    Write-Host $Text -ForegroundColor $Color
}

function Pause-Gate {
    Write-Host ""
    [void](Read-Host "Press Enter to return to Organism Gate")
}

function Invoke-PetriPreset {
    param([string]$Preset, [int]$Steps = 120, [int]$Grid = 56)
    Set-Location $Root
    Write-GateLine "Running preset: $Preset" "Cyan"
    & python -m petri_lab.cli --root . --preset $Preset --steps $Steps --grid $Grid --json
    if ($LASTEXITCODE -ne 0) { throw "Petri simulation failed for preset $Preset" }
    Pause-Gate
}

function Open-PetriElectron {
    Set-Location $Root
    if (-not (Test-Path -LiteralPath ".\electron\package.json")) {
        Write-GateLine "Electron package not found. Run the Python simulations first, or restore the electron folder." "Yellow"
        Pause-Gate
        return
    }
    Push-Location ".\electron"
    if (-not (Test-Path -LiteralPath ".\node_modules")) {
        Write-GateLine "Installing Electron dependencies..." "Yellow"
        & npm install
        if ($LASTEXITCODE -ne 0) { Pop-Location; throw "npm install failed" }
    }
    Write-GateLine "Opening Electron Microscope HUD..." "Cyan"
    & npm start
    Pop-Location
    Pause-Gate
}

function Open-Artifacts {
    Set-Location $Root
    $Path = Join-Path $Root "artifacts\bio\runs"
    if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Force -Path $Path | Out-Null }
    & explorer.exe $Path
}

function Show-LatestReceipt {
    Set-Location $Root
    $Path = Join-Path $Root "reports\bio\petri_summary_latest.md"
    if (Test-Path -LiteralPath $Path) { Get-Content -LiteralPath $Path -Raw | Write-Host }
    if (-not (Test-Path -LiteralPath $Path)) { Write-GateLine "No latest receipt yet. Run a preset first." "Yellow" }
    Pause-Gate
}

function Show-Roadmap {
    Set-Location $Root
    if (Test-Path -LiteralPath ".\ROADMAP.md") { Get-Content ".\ROADMAP.md" -Raw | Write-Host }
    Pause-Gate
}

while ($true) {
    Clear-Host
    Write-GateLine ""
    Write-GateLine "  ===============================================" "DarkCyan"
    Write-GateLine "      ORGANISM GATE  |  PETRI DISH PRO" "Cyan"
    Write-GateLine "  ===============================================" "DarkCyan"
    Write-GateLine "      models simulate -> humans validate -> receipts govern claims" "Gray"
    Write-GateLine ""
    Write-GateLine "  [1] Open Electron Microscope HUD" "White"
    Write-GateLine "  [2] Run Microbial Competition" "White"
    Write-GateLine "  [3] Run Antibiotic Selection" "White"
    Write-GateLine "  [4] Run Cellular Tissue Interaction" "White"
    Write-GateLine "  [5] Validation Tests" "White"
    Write-GateLine "  [6] Latest Run Receipt" "White"
    Write-GateLine "  [7] Open Artifact Folder" "White"
    Write-GateLine "  [8] Roadmap" "White"
    Write-GateLine "  [Q] Quit" "White"
    Write-GateLine ""
    $Choice = Read-Host "Select"

    if ($Choice -eq "1") { Open-PetriElectron }
    if ($Choice -eq "2") { Invoke-PetriPreset -Preset "microbial_competition" -Steps 120 -Grid 56 }
    if ($Choice -eq "3") { Invoke-PetriPreset -Preset "antibiotic_selection" -Steps 120 -Grid 56 }
    if ($Choice -eq "4") { Invoke-PetriPreset -Preset "cellular_tissue_interaction" -Steps 120 -Grid 56 }
    if ($Choice -eq "5") {
        Set-Location $Root
        & python -m unittest discover -s tests
        Pause-Gate
    }
    if ($Choice -eq "6") { Show-LatestReceipt }
    if ($Choice -eq "7") { Open-Artifacts }
    if ($Choice -eq "8") { Show-Roadmap }
    if ($Choice -match "^[Qq]$") { break }
}

Set-Location $Root
Write-GateLine "Organism Gate closed. Returned to repo root." "Green"
