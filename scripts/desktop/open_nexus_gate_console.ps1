param(
    [string]$RepoRoot = "",
    [switch]$InstallElectronDeps
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Continue"

function Write-NG {
    param([string]$Message)
    Write-Host ("[NG] {0}" -f $Message)
}

function Write-OK {
    param([string]$Message)
    Write-Host ("[OK] {0}" -f $Message)
}

function Write-FAIL {
    param([string]$Message)
    Write-Host ("[FAIL] {0}" -f $Message)
}

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

try {
    Set-Location $RepoRoot
}
catch {
    Write-FAIL ("Cannot enter repo root: {0}" -f $_.Exception.Message)
    Read-Host "Press Enter to close"
    exit 1
}

$NexusScript = Join-Path $RepoRoot "scripts\nexus.ps1"
$ElectronDir = Join-Path $RepoRoot "electron"
$ElectronPackage = Join-Path $ElectronDir "package.json"

if (-not (Test-Path -LiteralPath $NexusScript -PathType Leaf)) {
    Write-FAIL "scripts/nexus.ps1 not found"
    Read-Host "Press Enter to close"
    exit 1
}

function Invoke-NexusLane {
    param(
        [string]$Lane,
        [string]$Tag = ""
    )

    Write-Host ""
    Write-NG ("Running lane: {0}" -f $Lane)
    Write-NG "Boundary: recommendation-only surfaces; human authorizes durable mutation."
    Write-NG ("RepoRoot: {0}" -f $RepoRoot)

    $argsList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $NexusScript)

    if ($Lane -eq "ask") {
        if ([string]::IsNullOrWhiteSpace($Tag)) {
            $Tag = "What should we do next?"
        }
        $argsList += @("ask", "-Tag", $Tag)
    }
    else {
        $argsList += @($Lane)
    }

    & powershell @argsList
    $code = $LASTEXITCODE

    if ($code -eq 0) {
        Write-OK ("lane completed: {0}" -f $Lane)
    }
    else {
        Write-FAIL ("lane exited with code {0}: {1}" -f $code, $Lane)
    }

    Write-Host ""
    Read-Host "Press Enter to return to NEXUS menu"
}

function Invoke-OpenNexusGate {
    Write-Host ""
    Write-NG "Open NexusGate selected."
    Write-NG "Running Electron preflight through governed NEXUS lane first."

    & powershell -NoProfile -ExecutionPolicy Bypass -File $NexusScript electron-preflight
    $preflightCode = $LASTEXITCODE

    if ($preflightCode -ne 0) {
        Write-FAIL ("electron-preflight exited with code {0}" -f $preflightCode)
        $continue = Read-Host "Continue and attempt Electron UI anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            return
        }
    }

    if (-not (Test-Path -LiteralPath $ElectronPackage -PathType Leaf)) {
        Write-FAIL "electron/package.json not found."
        Read-Host "Press Enter to return to menu"
        return
    }

    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $npm) {
        $npm = Get-Command npm -ErrorAction SilentlyContinue
    }

    if (-not $npm) {
        Write-FAIL "npm was not found in PATH. Install Node.js or open the terminal TUI instead."
        Read-Host "Press Enter to return to menu"
        return
    }

    $nodeModules = Join-Path $ElectronDir "node_modules"
    if (-not (Test-Path -LiteralPath $nodeModules -PathType Container)) {
        Write-NG "Electron dependencies are not installed under electron/node_modules."
        if ($InstallElectronDeps.IsPresent) {
            $answer = "y"
        }
        else {
            $answer = Read-Host "Run npm install in electron now? (y/N)"
        }

        if ($answer -eq "y" -or $answer -eq "Y") {
            Push-Location $ElectronDir
            try {
                & $npm.Source install
                if ($LASTEXITCODE -ne 0) {
                    Write-FAIL ("npm install exited with code {0}" -f $LASTEXITCODE)
                    Read-Host "Press Enter to return to menu"
                    return
                }
            }
            finally {
                Pop-Location
            }
        }
        else {
            Write-NG "Electron open skipped. Dependencies are required for npm start."
            Read-Host "Press Enter to return to menu"
            return
        }
    }

    Write-NG "Opening Electron UI with npm start."
    Push-Location $ElectronDir
    try {
        & $npm.Source start
        $code = $LASTEXITCODE
        if ($code -eq 0) {
            Write-OK "Electron UI exited cleanly."
        }
        else {
            Write-FAIL ("Electron UI exited with code {0}" -f $code)
        }
    }
    finally {
        Pop-Location
    }

    Write-Host ""
    Read-Host "Press Enter to return to NEXUS menu"
}

function Show-Menu {
    Write-Host ""
    Write-Host "========================================"
    Write-Host " NEXUS GATE - Desktop Entry Portal"
    Write-Host "========================================"
    Write-Host "1. Open NexusGate"
    Write-Host "2. Status / health surface"
    Write-Host "3. Terminal TUI surface"
    Write-Host "4. NN router health"
    Write-Host "5. Ask NEXUS router"
    Write-Host "6. Open repo folder"
    Write-Host "Q. Quit"
    Write-Host ""
    Write-Host "Rule: models recommend; human authorizes durable mutation."
    Write-Host ""
}

Write-NG "NEXUS Gate launcher opened."
Write-NG "Primary entry: Open NexusGate -> Electron UI."

while ($true) {
    Show-Menu
    $choice = Read-Host "Choose"

    if ($choice -eq "1") {
        Invoke-OpenNexusGate
    }
    elseif ($choice -eq "2") {
        Invoke-NexusLane -Lane "status"
    }
    elseif ($choice -eq "3") {
        Invoke-NexusLane -Lane "tui"
    }
    elseif ($choice -eq "4") {
        Invoke-NexusLane -Lane "nn-health"
    }
    elseif ($choice -eq "5") {
        $tag = Read-Host "Ask"
        Invoke-NexusLane -Lane "ask" -Tag $tag
    }
    elseif ($choice -eq "6") {
        explorer.exe $RepoRoot | Out-Null
    }
    elseif ($choice -eq "Q" -or $choice -eq "q") {
        Write-OK "closing NEXUS Gate launcher"
        exit 0
    }
    else {
        Write-NG "Unknown choice."
    }
}
