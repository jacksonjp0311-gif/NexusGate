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

function Test-OllamaEndpoint {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    }
    catch {
        return $false
    }
}

function Resolve-OllamaExe {
    $candidates = @(
        $env:OLLAMA_EXE,
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama\Ollama.exe")
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    $cmd = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $cmd = Get-Command ollama -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    return ""
}

function Start-OllamaInnerBackend {
    Write-NG "Preparing local Ollama backend inside NEXUS entry portal."

    $env:CUDA_VISIBLE_DEVICES = "-1"
    $env:NEXUS_OLLAMA_NUM_GPU = "0"

    if ([string]::IsNullOrWhiteSpace($env:OLLAMA_MODELS)) {
        $env:OLLAMA_MODELS = Join-Path $env:USERPROFILE ".ollama\models"
    }

    if (Test-OllamaEndpoint) {
        Write-OK "Ollama backend already online at 127.0.0.1:11434."
        return $true
    }

    $ollamaExe = Resolve-OllamaExe
    if ([string]::IsNullOrWhiteSpace($ollamaExe)) {
        Write-FAIL "ollama.exe not found. Install Ollama or add it to PATH."
        return $false
    }

    Write-NG ("Starting hidden Ollama backend: {0}" -f $ollamaExe)
    Write-NG ("OLLAMA_MODELS: {0}" -f $env:OLLAMA_MODELS)
    Write-NG "CPU fallback: CUDA_VISIBLE_DEVICES=-1; NEXUS_OLLAMA_NUM_GPU=0"

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $ollamaExe
    $psi.Arguments = "serve"
    $psi.WorkingDirectory = $RepoRoot
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.EnvironmentVariables["CUDA_VISIBLE_DEVICES"] = "-1"
    $psi.EnvironmentVariables["NEXUS_OLLAMA_NUM_GPU"] = "0"
    $psi.EnvironmentVariables["OLLAMA_MODELS"] = $env:OLLAMA_MODELS

    try {
        $proc = [System.Diagnostics.Process]::Start($psi)
        Write-NG ("Ollama inner backend PID: {0}" -f $proc.Id)
    }
    catch {
        Write-FAIL ("Ollama backend start failed: {0}" -f $_.Exception.Message)
        return $false
    }

    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-OllamaEndpoint) {
            Write-OK "Ollama backend is online."
            return $true
        }
    }

    Write-FAIL "Ollama backend did not become ready in time."
    return $false
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

function Invoke-NexusRuntimeResidueClean {
    Write-Host ""
    Write-NG "Dev clean: restoring tracked generated runtime surfaces."

    git restore --worktree -- reports state ledger docs/feedback/FEEDBACK_LOG.md 2>$null

    $reportRoot = Join-Path $RepoRoot "reports"
    if (Test-Path -LiteralPath $reportRoot) {
        Get-ChildItem -Path $reportRoot -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^nexus_.*_report_20\d{6}_\d{6}\.json$' } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }

    $status = @(git status --short)
    if ($status.Count -eq 0) {
        Write-OK "Dev clean complete. Working tree is clean."
    }
    else {
        Write-NG "Dev clean complete with residue:"
        $status | ForEach-Object { Write-Host $_ }
    }

    Write-Host ""
    Read-Host "Press Enter to return to Dev Mode"
}

function Invoke-NexusCompilerSummary {
    Write-Host ""
    Write-NG "Dev compiler summary starting."
    Write-NG "This streams a compact compiler view into the dev console."

    $raw = python -m nexus_gate.compiler --root . --json | Out-String
    $code = $LASTEXITCODE

    if ($code -ne 0) {
        Write-FAIL ("compiler exited with code {0}" -f $code)
        Write-Host $raw
        Read-Host "Press Enter to return to Dev Mode"
        return
    }

    try {
        $compiled = $raw | ConvertFrom-Json
        $failed = @($compiled.gates | Where-Object { $_.status -ne "pass" })
        $unit = @($compiled.gates | Where-Object { $_.gate -eq "unit_tests" } | Select-Object -First 1)

        Write-OK ("Compiler status: {0}" -f $compiled.status)
        Write-NG ("Gate count: {0}" -f $compiled.gates.Count)
        Write-NG ("Failed gates: {0}" -f $failed.Count)

        if ($unit) {
            Write-NG ("Unit test gate: {0}" -f $unit.status)
            if ($unit.evidence.stderr_tail) {
                Write-Host ""
                Write-NG "Unit test tail:"
                Write-Host $unit.evidence.stderr_tail
            }
        }

        if ($failed.Count -gt 0) {
            Write-Host ""
            Write-FAIL "Failed gates:"
            $failed | ForEach-Object { Write-Host ("- {0}: {1}" -f $_.gate, $_.message) }
        }
    }
    catch {
        Write-FAIL ("compiler JSON parse failed: {0}" -f $_.Exception.Message)
        Write-Host $raw
    }

    Write-Host ""
    Read-Host "Press Enter to return to Dev Mode"
}

function Invoke-NexusFullTests {
    Write-Host ""
    Write-NG "Dev test run starting."

    python -m compileall nexus_gate tests
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "compileall failed"
        Read-Host "Press Enter to return to Dev Mode"
        return
    }

    python -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "unit tests failed"
        Read-Host "Press Enter to return to Dev Mode"
        return
    }

    Write-OK "Dev tests passed."
    Write-Host ""
    Read-Host "Press Enter to return to Dev Mode"
}

function Show-NexusGitStatus {
    Write-Host ""
    Write-NG "Dev git status:"
    $status = @(git status --short)
    if ($status.Count -eq 0) {
        Write-OK "working tree clean"
    }
    else {
        $status | ForEach-Object { Write-Host $_ }
    }

    Write-Host ""
    Read-Host "Press Enter to return to Dev Mode"
}

function Show-LatestHandoffReport {
    Write-Host ""
    Write-NG "Latest HANDOFF report:"

    $queue = Join-Path $RepoRoot "reports\handoff_queue"
    if (-not (Test-Path -LiteralPath $queue)) {
        Write-NG "No handoff_queue folder found yet."
        Read-Host "Press Enter to return to Dev Mode"
        return
    }

    $latest = Get-ChildItem -Path $queue -Recurse -Filter "handoff_action_report.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latest) {
        Write-NG "No HANDOFF action report found yet."
        Read-Host "Press Enter to return to Dev Mode"
        return
    }

    Write-OK ("Report: {0}" -f $latest.FullName)
    Get-Content -LiteralPath $latest.FullName -Raw | Write-Host

    Write-Host ""
    Read-Host "Press Enter to return to Dev Mode"
}

function Invoke-NexusDevMode {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUS DEV MODE - Handoff Console"
        Write-Host "========================================"
        Write-Host "1. Git status"
        Write-Host "2. Clean runtime residue"
        Write-Host "3. Compiler summary"
        Write-Host "4. Full tests"
        Write-Host "5. Latest HANDOFF report"
        Write-Host "6. Open full Electron UI"
        Write-Host "B. Back to main menu"
        Write-Host ""
        Write-Host "Rule: dev mode streams local evidence; human authorizes durable mutation."
        Write-Host ""

        $devChoice = Read-Host "Dev"

        if ($devChoice -eq "1") {
            Show-NexusGitStatus
        }
        elseif ($devChoice -eq "2") {
            Invoke-NexusRuntimeResidueClean
        }
        elseif ($devChoice -eq "3") {
            Invoke-NexusCompilerSummary
        }
        elseif ($devChoice -eq "4") {
            Invoke-NexusFullTests
        }
        elseif ($devChoice -eq "5") {
            Show-LatestHandoffReport
        }
        elseif ($devChoice -eq "6") {
            Invoke-OpenNexusGate
        }
        elseif ($devChoice -eq "B" -or $devChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown Dev Mode choice."
        }
    }
}
function Show-Menu {
    Write-Host ""
    Write-Host "========================================"
    Write-Host " NEXUS GATE - Desktop Entry Portal"
    Write-Host "========================================"
    Write-Host "1. Open NexusGate"
    Write-Host "2. Dev Mode / Handoff Console"
    Write-Host "3. Status / health surface"
    Write-Host "4. Terminal TUI surface"
    Write-Host "5. NN router health"
    Write-Host "6. Ask NEXUS router"
    Write-Host "7. Open repo folder"
    Write-Host "Q. Quit"
    Write-Host ""
    Write-Host "Rule: models recommend; human authorizes durable mutation."
    Write-Host ""
}

Write-NG "NEXUS Gate launcher opened."
Write-NG "Primary entry: Open NexusGate -> Electron UI."
Write-NG "Dev entry: Dev Mode / Handoff Console -> patch, compiler, wound evidence."

while ($true) {
    Show-Menu
    $choice = Read-Host "Choose"

    if ($choice -eq "1") {
        Invoke-OpenNexusGate
    }
    elseif ($choice -eq "2") {
        Invoke-NexusDevMode
    }
    elseif ($choice -eq "3") {
        Invoke-NexusLane -Lane "status"
    }
    elseif ($choice -eq "4") {
        Invoke-NexusLane -Lane "tui"
    }
    elseif ($choice -eq "5") {
        Invoke-NexusLane -Lane "nn-health"
    }
    elseif ($choice -eq "6") {
        $tag = Read-Host "Ask"
        Invoke-NexusLane -Lane "ask" -Tag $tag
    }
    elseif ($choice -eq "7") {
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
