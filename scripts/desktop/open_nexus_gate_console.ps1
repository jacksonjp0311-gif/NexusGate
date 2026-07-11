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
$GitHubRepoUrl = "https://github.com/jacksonjp0311-gif/NexusGate"

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

    Write-NG "Dev clean: removing untracked timestamped report JSON files only."

    $untrackedReports = @(
        git ls-files --others --exclude-standard -- reports |
            Where-Object { $_ -match '^reports/nexus_.*_report_20\d{6}_\d{6}\.json$' }
    )

    foreach ($relative in $untrackedReports) {
        $normalized = $relative.Replace('/', '\')
        $fullPath = Join-Path $RepoRoot $normalized
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            Remove-Item -LiteralPath $fullPath -Force -ErrorAction SilentlyContinue
        }
    }

    if ($untrackedReports.Count -gt 0) {
        Write-OK ("Removed untracked timestamped report files: {0}" -f $untrackedReports.Count)
    }
    else {
        Write-NG "No untracked timestamped report files found."
    }

    Write-NG "Dev clean: second safety restore for tracked generated surfaces."
    git restore --worktree -- reports state ledger docs/feedback/FEEDBACK_LOG.md 2>$null

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

function Get-NexusFailureModeIndex {
    $path = Join-Path $RepoRoot "state\failure_modes\nexus_failure_modes.v0.7.9.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Write-FAIL ("Failure mode index missing: {0}" -f $path)
        return $null
    }

    try {
        return (Get-Content -LiteralPath $path -Raw | ConvertFrom-Json)
    }
    catch {
        Write-FAIL ("Failure mode index parse failed: {0}" -f $_.Exception.Message)
        return $null
    }
}

function Get-NexusLatestHandoffReportText {
    $queue = Join-Path $RepoRoot "reports\handoff_queue"
    if (-not (Test-Path -LiteralPath $queue)) { return "" }

    $latest = Get-ChildItem -Path $queue -Recurse -Filter "handoff_action_report.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latest) { return "" }

    try { return (Get-Content -LiteralPath $latest.FullName -Raw) }
    catch { return "" }
}

function Get-NexusFailureDoctorClassification {
    $index = Get-NexusFailureModeIndex
    if (-not $index) { return @() }

    $statusText = (@(git status --short) -join "`n")
    $handoffText = Get-NexusLatestHandoffReportText
    $scanText = ($statusText + "`n" + $handoffText)

    $matches = New-Object System.Collections.Generic.List[object]

    foreach ($entry in @($index.modes | Sort-Object n)) {
        foreach ($sign in @($entry.signs)) {
            if ($scanText -like ("*" + $sign + "*")) {
                $matches.Add($entry) | Out-Null
                break
            }
        }
    }

    return @($matches)
}

function Show-NexusFailureModes {
    $index = Get-NexusFailureModeIndex
    if (-not $index) {
        Read-Host "Press Enter to return to Failure Modes"
        return
    }

    Write-Host ""
    Write-NG ("Failure Mode Index: {0}" -f $index.version)
    Write-NG "Syntax: FM := id,key,n,who,why,what,when,signs,doctor,retry,authority"
    Write-Host ""

    foreach ($entry in @($index.modes | Sort-Object n)) {
        Write-Host ("{0}  {1}" -f $entry.id, $entry.key) -ForegroundColor Yellow
        Write-Host ("  who : {0}" -f $entry.who)
        Write-Host ("  why : {0}" -f $entry.why)
        Write-Host ("  what: {0}" -f $entry.what)
        Write-Host ("  when: {0}" -f $entry.when)
        Write-Host ("  fix : {0}" -f $entry.doctor) -ForegroundColor Cyan
        Write-Host ("  retry: {0}" -f $entry.retry) -ForegroundColor Green
        Write-Host ("  auth: {0}" -f $entry.authority)
        Write-Host ""
    }

    Read-Host "Press Enter to return to Failure Modes"
}

function Invoke-NexusFailureDoctorScan {
    Write-Host ""
    Write-NG "Failure Doctor scan starting."
    Write-NG "Mode: read/classify/recommend. Durable source mutation is locked."

    $matches = @(Get-NexusFailureDoctorClassification)
    $status = @(git status --short)

    Write-Host ""
    Write-Host "NEXUS FAILURE DOCTOR REPORT" -ForegroundColor Yellow
    Write-Host "==========================="
    Write-Host ("worktree-clean: {0}" -f ($status.Count -eq 0))
    Write-Host ("matched-modes: {0}" -f $matches.Count)
    Write-Host ""

    if ($matches.Count -eq 0) {
        Write-OK "No known failure mode matched current git status or latest HANDOFF report."
        Write-NG "Next: run compiler summary or full tests if validating a patch."
    }
    else {
        foreach ($entry in $matches) {
            Write-Host ("MODE: {0} / {1}" -f $entry.id, $entry.key) -ForegroundColor Yellow
            Write-Host ("  who : {0}" -f $entry.who)
            Write-Host ("  why : {0}" -f $entry.why)
            Write-Host ("  what: {0}" -f $entry.what)
            Write-Host ("  when: {0}" -f $entry.when)
            Write-Host ("  doctor: {0}" -f $entry.doctor) -ForegroundColor Cyan
            Write-Host ("  retry : {0}" -f $entry.retry) -ForegroundColor Green
            Write-Host ("  auth  : {0}" -f $entry.authority)
            Write-Host ""
        }
    }

    Write-Host "Boundary: Doctor classifies and recommends. It does not self-authorize repairs."
    Write-Host ""
    Read-Host "Press Enter to return to Failure Modes"
}

function Invoke-NexusFailureDoctorSafeClean {
    Write-Host ""
    Write-NG "Failure Doctor safe clean selected by human."
    Write-NG "Restoring tracked generated surfaces."

    git restore --worktree -- reports state ledger docs/feedback/FEEDBACK_LOG.md 2>$null

    Write-NG "Removing untracked timestamped report JSON files only."
    $untrackedReports = @(
        git ls-files --others --exclude-standard -- reports |
            Where-Object { $_ -match '^reports/nexus_.*_report_20\d{6}_\d{6}\.json$' }
    )

    foreach ($relative in $untrackedReports) {
        $normalized = $relative.Replace("/", "\")
        $fullPath = Join-Path $RepoRoot $normalized
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            Remove-Item -LiteralPath $fullPath -Force -ErrorAction SilentlyContinue
        }
    }

    git restore --worktree -- reports state ledger docs/feedback/FEEDBACK_LOG.md 2>$null

    $status = @(git status --short)
    if ($status.Count -eq 0) {
        Write-OK "Failure Doctor safe clean complete. Working tree is clean."
    }
    else {
        Write-NG "Failure Doctor safe clean complete with residue:"
        $status | ForEach-Object { Write-Host $_ }
    }

    Write-Host ""
    Read-Host "Press Enter to return to Failure Modes"
}

function Invoke-NexusFailureDoctorRetry {
    Write-Host ""
    Write-NG "Failure Doctor retry checks starting."
    Write-NG "Retry is validation-only. It does not patch source."

    powershell -NoProfile -ExecutionPolicy Bypass -Command {
        $null = [scriptblock]::Create((Get-Content -Raw "scripts\desktop\open_nexus_gate_console.ps1"))
        Write-Host "[OK] launcher parses"
    }

    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "launcher parse retry failed"
        Read-Host "Press Enter to return to Failure Modes"
        return
    }

    python -m unittest discover -s tests -p test_failure_mode_doctor_gateway.py -v
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "Failure Mode Doctor tests failed"
        Read-Host "Press Enter to return to Failure Modes"
        return
    }

    python -m nexus_gate.compiler --root . --json
    if ($LASTEXITCODE -ne 0) {
        Write-FAIL "NEXUS compiler retry failed"
        Read-Host "Press Enter to return to Failure Modes"
        return
    }

    Write-OK "Failure Doctor retry checks passed."
    Write-Host ""
    Read-Host "Press Enter to return to Failure Modes"
}

function Invoke-NexusFailureModeDoctorConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUS FAILURE MODES / DOCTOR"
        Write-Host "========================================"
        Write-Host "1. List ordered failure modes"
        Write-Host "2. Doctor scan current state"
        Write-Host "3. Safe clean generated residue"
        Write-Host "4. Retry validation checks"
        Write-Host "B. Back to main menu"
        Write-Host ""
        Write-Host "Rule: Doctor classifies and recommends; human authorizes repair."
        Write-Host ""

        $doctorChoice = Read-Host "Doctor"

        if ($doctorChoice -eq "1") {
            Show-NexusFailureModes
        }
        elseif ($doctorChoice -eq "2") {
            Invoke-NexusFailureDoctorScan
        }
        elseif ($doctorChoice -eq "3") {
            Invoke-NexusFailureDoctorSafeClean
        }
        elseif ($doctorChoice -eq "4") {
            Invoke-NexusFailureDoctorRetry
        }
        elseif ($doctorChoice -eq "B" -or $doctorChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown Failure Doctor choice."
        }
    }
}



function Invoke-NexusCellConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUSCELL / EXECUTION CONTAINMENT"
        Write-Host "========================================"
        Write-Host "1. Open local NexusCell folder"
        Write-Host "2. Open NexusCell architecture doc"
        Write-Host "3. Open GitHub NexusCell architecture"
        Write-Host "4. Show compact NexusCell laws"
        Write-Host "5. Show NexusCell manifest"
        Write-Host "6. Plan gated invocation (read-only)"
        Write-Host "7. Build context bridge packet (read-only)"
        Write-Host "8. Build core bridge packet (read-only)"
        Write-Host "9. Build full core run packet (controlled, no execute by default)"
        Write-Host "B. Back to main menu"
        Write-Host ""
        Write-Host "Rule: NexusCell governs execution; no backend executes without explicit authority."
        Write-Host ""

        $cellChoice = Read-Host "NexusCell"

        if ($cellChoice -eq "1") {
            explorer.exe (Join-Path $RepoRoot "NexusCell") | Out-Null
        }
        elseif ($cellChoice -eq "2") {
            explorer.exe (Join-Path $RepoRoot "docs\nexus_cell\NEXUS_CELL_ARCHITECTURE.md") | Out-Null
        }
        elseif ($cellChoice -eq "3") {
            Invoke-NexusOpenUrl ($GitHubRepoUrl + "/blob/main/docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        }
        elseif ($cellChoice -eq "4") {
            Write-Host ""
            Write-NG "NexusCell compact laws:"
            Write-Host "A sandbox contains code." -ForegroundColor Green
            Write-Host "NexusCell governs execution." -ForegroundColor Green
            Write-Host "No execution without containment." -ForegroundColor Yellow
            Write-Host "No containment without authority." -ForegroundColor Yellow
            Write-Host "No authority without evidence." -ForegroundColor Yellow
            Write-Host "No evidence without ledger." -ForegroundColor Yellow
            Write-Host "No ledger without compiler visibility." -ForegroundColor Yellow
            Write-Host "No compounding without human authorization." -ForegroundColor Yellow
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "5") {
            $manifestPath = Join-Path $RepoRoot "state\nexus_cell\cell_manifest.v0.8.4.json"
            Write-Host ""
            if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
                Get-Content -LiteralPath $manifestPath -Raw | Write-Host
            }
            else {
                Write-NG "NexusCell manifest has not been created yet."
            }
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "6") {
            $intent = Read-Host "Intent to plan"
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-plan -Tag $intent
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "7") {
            $intent = Read-Host "Intent to bridge"
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-context -Tag $intent
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "8") {
            $intent = Read-Host "Intent to bridge through NexusCell core"
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-bridge -Tag $intent
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "9") {
            $lane = Read-Host "Controlled lane (status/compile/tests/cell-plan/cell-context/cell-bridge)"
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-run -Tag $lane
            Write-Host ""
            Read-Host "Press Enter to return to NexusCell"
        }
        elseif ($cellChoice -eq "B" -or $cellChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown NexusCell choice."
        }
    }
}

function Invoke-NexusShellConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUSSHELL / OPERATOR"
        Write-Host "========================================"
        Write-Host "1. Build shell status packet"
        Write-Host "2. Build shell handoff packet"
        Write-Host "3. Open NexusShell docs"
        Write-Host "4. Open NexusShell folder"
        Write-Host "B. Back to main menu"
        Write-Host ""
        Write-Host "Rule: NexusShell routes governed lanes; it does not self-authorize execution."
        Write-Host ""

        $shellChoice = Read-Host "NexusShell"

        if ($shellChoice -eq "1") {
            $intent = Read-Host "Intent"
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts/nexus.ps1") shell -Tag $intent
            Write-Host ""
            Read-Host "Press Enter to return to NexusShell"
        }
        elseif ($shellChoice -eq "2") {
            $intent = Read-Host "Handoff intent"
            python -m nexus_gate.nexus_shell.shell --root $RepoRoot --command handoff --intent $intent --json
            Write-Host ""
            Read-Host "Press Enter to return to NexusShell"
        }
        elseif ($shellChoice -eq "3") {
            explorer.exe (Join-Path $RepoRoot "docs/nexus_shell/NEXUS_SHELL_OPERATOR.md") | Out-Null
        }
        elseif ($shellChoice -eq "4") {
            explorer.exe (Join-Path $RepoRoot "NexusShell") | Out-Null
        }
        elseif ($shellChoice -eq "B" -or $shellChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown NexusShell choice."
        }
    }
}

function Invoke-NexusCellExecutionGateConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NexusCell - Containment Cell / Execution Gate"
        Write-Host "========================================"
        Write-Host "1. NexusCell doctor"
        Write-Host "2. NexusCell run hello payload"
        Write-Host "3. NexusCell ledger"
        Write-Host "4. NexusCell policy"
        Write-Host "B. Back"
        Write-Host ""
        Write-Host "Rule: local evidence, human authorization, no autonomous mutation, compiler/evolve gates."
        Write-Host ""
        $cellGateChoice = Read-Host "NexusCell Gate"
        if ($cellGateChoice -eq "1") {
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-doctor
            Read-Host "Press Enter to return to NexusCell Gate"
        }
        elseif ($cellGateChoice -eq "2") {
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-run
            Read-Host "Press Enter to return to NexusCell Gate"
        }
        elseif ($cellGateChoice -eq "3") {
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-ledger
            Read-Host "Press Enter to return to NexusCell Gate"
        }
        elseif ($cellGateChoice -eq "4") {
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\nexus.ps1") cell-policy
            Read-Host "Press Enter to return to NexusCell Gate"
        }
        elseif ($cellGateChoice -eq "B" -or $cellGateChoice -eq "b") { return }
        else { Write-NG "Unknown NexusCell Gate choice." }
    }
}

function Invoke-NexusNeuralActivity {
    Write-Host ""
    Write-NG "Opening Neural Activity / Neural Cathedral."
    Write-NG "Boundary: visual surface only; no execution authority changes."

    $neuralPath = Join-Path $RepoRoot "neural_activity\index.html"

    if (-not (Test-Path -LiteralPath $neuralPath -PathType Leaf)) {
        Write-FAIL ("Neural Activity entrypoint missing: {0}" -f $neuralPath)
        Read-Host "Press Enter to return to NEXUS menu"
        return
    }

    try {
        & rundll32.exe url.dll,FileProtocolHandler $neuralPath
        Write-OK "Neural Activity open request sent."
    }
    catch {
        Write-FAIL ("Could not open Neural Activity: {0}" -f $_.Exception.Message)
    }

    Write-Host ""
    Read-Host "Press Enter to return to NEXUS menu"
}

function Invoke-NexusPetriDishPortal {
    $petriRoot = Join-Path $RepoRoot "PetriDishPro"
    $petriElectron = Join-Path $petriRoot "electron"

    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " ORGANISM GATE | PETRI DISH PRO"
        Write-Host "========================================"
        Write-Host "models simulate -> humans validate -> receipts govern claims"
        Write-Host ""
        Write-Host "[1] Open Electron Microscope HUD"
        Write-Host "[2] Run Microbial Competition"
        Write-Host "[3] Run Antibiotic Selection"
        Write-Host "[4] Run Cellular Tissue Interaction"
        Write-Host "[5] Validation Tests"
        Write-Host "[6] Latest Run Receipt"
        Write-Host "[7] Open Artifact Folder"
        Write-Host "[8] Roadmap"
        Write-Host "[B] Back to NEXUS"
        Write-Host ""
        Write-Host "Boundary: deterministic simulation evidence only; no medical, wet-lab, or species-identification authority."
        Write-Host ""

        $petriChoice = Read-Host "PetriDishPortal"

        if ($petriChoice -eq "1") {
            if (-not (Test-Path -LiteralPath (Join-Path $petriElectron "package.json") -PathType Leaf)) {
                Write-FAIL ("Petri Electron package missing: {0}" -f $petriElectron)
                Read-Host "Press Enter to return to PetriDishPortal"
                continue
            }
            Push-Location $petriElectron
            try { npm start }
            finally { Pop-Location }
            Read-Host "Press Enter to return to PetriDishPortal"
        }
        elseif ($petriChoice -eq "2" -or $petriChoice -eq "3" -or $petriChoice -eq "4") {
            $preset = "microbial_competition"
            if ($petriChoice -eq "3") { $preset = "antibiotic_selection" }
            if ($petriChoice -eq "4") { $preset = "cellular_tissue_interaction" }
            Push-Location $petriRoot
            try {
                python -m petri_lab.cli --root . --preset $preset --steps 120 --grid 64 --json
            }
            finally { Pop-Location }
            Read-Host "Press Enter to return to PetriDishPortal"
        }
        elseif ($petriChoice -eq "5") {
            Push-Location $petriRoot
            try { python -m unittest discover -s tests }
            finally { Pop-Location }
            Read-Host "Press Enter to return to PetriDishPortal"
        }
        elseif ($petriChoice -eq "6") {
            $receipt = Join-Path $petriRoot "reports\bio\petri_particle_state_latest.json"
            if (Test-Path -LiteralPath $receipt -PathType Leaf) {
                Get-Content -LiteralPath $receipt -Raw | Write-Host
            }
            else {
                Write-NG "No Petri receipt found yet."
            }
            Read-Host "Press Enter to return to PetriDishPortal"
        }
        elseif ($petriChoice -eq "7") {
            explorer.exe (Join-Path $petriRoot "artifacts\bio\runs") | Out-Null
        }
        elseif ($petriChoice -eq "8") {
            explorer.exe (Join-Path $petriRoot "ROADMAP.md") | Out-Null
        }
        elseif ($petriChoice -eq "B" -or $petriChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown PetriDishPortal choice."
        }
    }
}

function Invoke-NexusT3mp3stPortal {
    $tempestRoot = Join-Path $RepoRoot "T3MP3ST"

    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " T3MP3ST | AUTHORIZED SECURITY LAB"
        Write-Host "========================================"
        Write-Host "models recommend -> humans scope -> receipts govern claims"
        Write-Host ""
        Write-Host "[1] Open Full UI / War Room"
        Write-Host "[2] Install dependencies"
        Write-Host "[3] Doctor"
        Write-Host "[4] Smoke"
        Write-Host "[5] Verify Claims"
        Write-Host "[6] Open Artifact Folder"
        Write-Host "[7] Open README"
        Write-Host "[B] Back to NEXUS"
        Write-Host ""
        Write-Host "Boundary: authorized targets only; no autonomous offensive action, secret exfiltration, or arbitrary shell."
        Write-Host ""

        $tempestChoice = Read-Host "T3MP3ST"

        if (-not (Test-Path -LiteralPath (Join-Path $tempestRoot "package.json") -PathType Leaf)) {
            Write-FAIL ("T3MP3ST package missing: {0}" -f $tempestRoot)
            Read-Host "Press Enter to return to NEXUS menu"
            return
        }

        if ($tempestChoice -eq "1") {
            $cmd = "Set-Location -LiteralPath '$tempestRoot'; npm run server"
            Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $cmd | Out-Null
            Start-Sleep -Seconds 2
            Start-Process "http://127.0.0.1:3333/ui/" | Out-Null
        }
        elseif ($tempestChoice -eq "2") {
            Push-Location $tempestRoot
            try { npm install }
            finally { Pop-Location }
            Read-Host "Press Enter to return to T3MP3ST"
        }
        elseif ($tempestChoice -eq "3") {
            Push-Location $tempestRoot
            try { npm run doctor }
            finally { Pop-Location }
            Read-Host "Press Enter to return to T3MP3ST"
        }
        elseif ($tempestChoice -eq "4") {
            Push-Location $tempestRoot
            try { npm run smoke }
            finally { Pop-Location }
            Read-Host "Press Enter to return to T3MP3ST"
        }
        elseif ($tempestChoice -eq "5") {
            Push-Location $tempestRoot
            try { npm run verify-claims }
            finally { Pop-Location }
            Read-Host "Press Enter to return to T3MP3ST"
        }
        elseif ($tempestChoice -eq "6") {
            explorer.exe $tempestRoot | Out-Null
        }
        elseif ($tempestChoice -eq "7") {
            explorer.exe (Join-Path $tempestRoot "README.md") | Out-Null
        }
        elseif ($tempestChoice -eq "B" -or $tempestChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown T3MP3ST choice."
        }
    }
}

function Invoke-NexusOpenUrl {
    param([string]$Url)
    Write-NG ("Opening: {0}" -f $Url)
    try {
        & rundll32.exe url.dll,FileProtocolHandler $Url
    }
    catch {
        Write-FAIL ("Could not open URL: {0}" -f $_.Exception.Message)
    }
}

function Invoke-NexusResourceMenu {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUS GITHUB / README / DOCS"
        Write-Host "========================================"
        Write-Host "1. Open GitHub repository"
        Write-Host "2. Open GitHub README"
        Write-Host "3. Open docs/ENTRYPOINTS.md"
        Write-Host "4. Open docs/versioning/NEXUS_CHANGELOG.md"
        Write-Host "5. Open local README.md"
        Write-Host "6. Open local docs folder"
        Write-Host "B. Back to main menu"
        Write-Host ""
        Write-Host "Rule: docs orient; human authorizes durable mutation."
        Write-Host ""

        $resourceChoice = Read-Host "Docs"

        if ($resourceChoice -eq "1") {
            Invoke-NexusOpenUrl $GitHubRepoUrl
        }
        elseif ($resourceChoice -eq "2") {
            Invoke-NexusOpenUrl ($GitHubRepoUrl + "/blob/main/README.md")
        }
        elseif ($resourceChoice -eq "3") {
            Invoke-NexusOpenUrl ($GitHubRepoUrl + "/blob/main/docs/ENTRYPOINTS.md")
        }
        elseif ($resourceChoice -eq "4") {
            Invoke-NexusOpenUrl ($GitHubRepoUrl + "/blob/main/docs/versioning/NEXUS_CHANGELOG.md")
        }
        elseif ($resourceChoice -eq "5") {
            explorer.exe (Join-Path $RepoRoot "README.md") | Out-Null
        }
        elseif ($resourceChoice -eq "6") {
            explorer.exe (Join-Path $RepoRoot "docs") | Out-Null
        }
        elseif ($resourceChoice -eq "B" -or $resourceChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown Docs choice."
        }
    }
}


function Invoke-NexusLoopCardsConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUS LOOPS / HUD CARDS"
        Write-Host "========================================"
        Write-Host "Rule: loop cards describe governed loops; they do not self-authorize execution."
        Write-Host ""

        $latestPath = Join-Path $RepoRoot "state\loops\nexus_loop_cards_latest.json"
        $versionedPath = Join-Path $RepoRoot "state\loops\nexus_loop_cards.v0.9.1B.json"
        $cardsPath = $latestPath
        if (-not (Test-Path -LiteralPath $cardsPath -PathType Leaf)) {
            $cardsPath = $versionedPath
        }

        if (-not (Test-Path -LiteralPath $cardsPath -PathType Leaf)) {
            Write-FAIL ("Loop card packet missing: {0}" -f $cardsPath)
            Write-NG "Choose R to rebuild from loops/nexus_loop_registry.v0.1.json."
        }
        else {
            try {
                $packet = Get-Content -LiteralPath $cardsPath -Raw | ConvertFrom-Json
                Write-OK ("Loop card packet: {0} cards" -f $packet.card_count)
                Write-NG ("Source registry: {0}" -f $packet.source_registry)
                Write-Host ""
                foreach ($card in @($packet.cards | Sort-Object order)) {
                    $fn = $card.PSObject.Properties["function"].Value
                    Write-Host ("[{0}] {1}" -f $card.order, $card.title) -ForegroundColor Cyan
                    Write-Host ("  loop    : {0}" -f $card.loop_id)
                    Write-Host ("  function: {0}" -f $fn)
                    Write-Host ("  use     : {0}" -f $card.operator_use)
                    Write-Host ("  command : {0}" -f $card.command_surface) -ForegroundColor Blue
                    Write-Host ("  auth    : human_required={0}; mutates={1}; stop_on_failure={2}" -f $card.requires_human_authorization, $card.mutates, $card.stop_on_failure)
                    Write-Host ""
                }
            }
            catch {
                Write-FAIL ("Loop card JSON parse failed: {0}" -f $_.Exception.Message)
            }
        }

        Write-Host "R. Rebuild loop cards from registry"
        Write-Host "J. Open loop card JSON"
        Write-Host "D. Open loop card docs"
        Write-Host "B. Back to main menu"
        Write-Host ""
        $loopChoice = Read-Host "Loop Cards"

        if ($loopChoice -eq "R" -or $loopChoice -eq "r") {
            python -m nexus_gate.loops.cards --root $RepoRoot --json | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-OK "Loop cards rebuilt." } else { Write-FAIL "Loop card rebuild failed." }
            Read-Host "Press Enter to continue"
        }
        elseif ($loopChoice -eq "J" -or $loopChoice -eq "j") {
            if (Test-Path -LiteralPath $cardsPath -PathType Leaf) { explorer.exe $cardsPath | Out-Null }
        }
        elseif ($loopChoice -eq "D" -or $loopChoice -eq "d") {
            explorer.exe (Join-Path $RepoRoot "docs\runtime\NEXUS_LOOP_CARDS.md") | Out-Null
        }
        elseif ($loopChoice -eq "B" -or $loopChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown Loop Cards choice."
        }
    }
}

function Invoke-NexusAlgorithmCardsConsole {
    while ($true) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " NEXUS ALGORITHM CARDS"
        Write-Host "========================================"
        Write-Host "Rule: algorithm cards preserve reasoning procedures; they do not self-authorize mutation."
        Write-Host ""

        $cardsPath = Join-Path $RepoRoot "state\algorithms\nexus_algorithm_cards_latest.json"

        if (-not (Test-Path -LiteralPath $cardsPath -PathType Leaf)) {
            Write-FAIL ("Algorithm card packet missing: {0}" -f $cardsPath)
            Write-NG "Choose R to rebuild from docs/algorithms/NEXUS_CORE_ALGORITHMS.md."
        }
        else {
            try {
                $packet = Get-Content -LiteralPath $cardsPath -Raw | ConvertFrom-Json
                Write-OK ("Algorithm card packet: {0} cards" -f $packet.card_count)
                Write-NG ("Source doc: {0}" -f $packet.source_doc)
                Write-Host ""
                foreach ($card in @($packet.cards | Sort-Object order)) {
                    Write-Host ("[{0}] {1}" -f $card.order, $card.title) -ForegroundColor Cyan
                    Write-Host ("  id      : {0}" -f $card.algorithm_id)
                    Write-Host ("  flow    : {0}" -f $card.flow)
                    Write-Host ("  use     : {0}" -f $card.operator_use)
                    Write-Host ("  outputs : {0}" -f (@($card.outputs) -join ", ")) -ForegroundColor Blue
                    Write-Host ""
                }
            }
            catch {
                Write-FAIL ("Algorithm card JSON parse failed: {0}" -f $_.Exception.Message)
            }
        }

        Write-Host "R. Rebuild algorithm cards from docs"
        Write-Host "J. Open algorithm card JSON"
        Write-Host "D. Open algorithm card docs"
        Write-Host "B. Back to main menu"
        Write-Host ""
        $algorithmChoice = Read-Host "Algorithm Cards"

        if ($algorithmChoice -eq "R" -or $algorithmChoice -eq "r") {
            python -m nexus_gate.algorithms.cards --root $RepoRoot --json | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-OK "Algorithm cards rebuilt." } else { Write-FAIL "Algorithm card rebuild failed." }
            Read-Host "Press Enter to continue"
        }
        elseif ($algorithmChoice -eq "J" -or $algorithmChoice -eq "j") {
            if (Test-Path -LiteralPath $cardsPath -PathType Leaf) { explorer.exe $cardsPath | Out-Null }
        }
        elseif ($algorithmChoice -eq "D" -or $algorithmChoice -eq "d") {
            explorer.exe (Join-Path $RepoRoot "docs\runtime\NEXUS_ALGORITHM_CARDS.md") | Out-Null
        }
        elseif ($algorithmChoice -eq "B" -or $algorithmChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown Algorithm Cards choice."
        }
    }
}

function Write-Portal {
    param(
        [string]$Text,
        [string]$Color = "Cyan"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Show-Menu {
    Clear-Host
    try {
        $Host.UI.RawUI.WindowTitle = "NEXUS GATE :: SPIRAL CORE PORTAL"
    }
    catch {}

    # NEXUS_SPIRAL_CORE_ASCII_BEGIN
    Write-Portal "========================================================================================================================" "Cyan"
    Write-Portal "        N E X U S   G A T E    ::    S P I R A L   C O R E   P O R T A L" "Cyan"
    Write-Portal "========================================================================================================================" "Cyan"
    Write-Host ""
    Write-Portal "                         [    ""WE DO NOT OBEY CHAOS. WE GOVERN THRESHOLDS.""    ]" "Blue"
    Write-Portal "                         [    ""AUTHORITY IS EARNED. ACCESS IS EVIDENCE.""       ]" "Blue"
    Write-Host ""
    Write-Portal "          .       +            .                 .                 .            +       ." "Cyan"
    Write-Portal "                .                 .:::::--------------:::::.                 ." "Cyan"
    Write-Portal "     +                     .::----:::::::........:::::::----::.                     +" "Cyan"
    Write-Portal "             .        .:---:::..      .:-=+********+=-:.      ..:::---:.        ." "Cyan"
    Write-Portal "                  .:---::.       .:-+*################*+-:.       .::---:." "Cyan"
    Write-Portal "   01110010 01101111  .::.   .:=*######*+=--::::--=+*######*=:.   .::.  01110010 01100101" "Blue"
    Write-Portal "              .   .:::.  .-+####*=-.      .::::.      .-=*####+-.  .:::.   ." "Cyan"
    Write-Portal "        +        .:::.  :=*###*-.     .-=*######*=-.     .-*###*=:  .:::.        +" "Cyan"
    Write-Portal "               .:::.  -+###=.     .:=*###*+==+*###*=:.     .=###+-  .:::.       ." "Cyan"
    Write-Portal "             . .:::. :=###+.     :=*##*=:  .  :=*##*=:     .+###=: .:::. ." "Cyan"
    Write-Portal "      01100001 .:::. -###=.     -###*-.   (  )   .-*###-     .=###- .:::. 01101100" "Blue"
    Write-Portal "             . .:::. :=###+.     :=*##*=:  ''  :=*##*=:     .+###=: .:::. ." "Cyan"
    Write-Portal "               .:::.  -+###=.     .:=*###*+==+*###*=:.     .=###+-  .:::.       ." "Cyan"
    Write-Portal "        +        .:::.  :=*###*-.     .-=*######*=-.     .-*###*=:  .:::.        +" "Cyan"
    Write-Portal "              .   .:::.  .-+####*=-.      .::::.      .-=*####+-.  .:::.   ." "Cyan"
    Write-Portal "   01100111 01100001  .::.   .:=*######*+=--::::--=+*######*=:.   .::.  01100111 01100101" "Blue"
    Write-Portal "                  .:---::.       .:-+*################*+-:.       .::---:." "Cyan"
    Write-Portal "             .        .:---:::..      .:-=+********+=-:.      ..:::---:.        ." "Cyan"
    Write-Portal "     +                     .::----:::::::........:::::::----::.                     +" "Cyan"
    Write-Portal "                .                 .:::::--------------:::::.                 ." "Cyan"
    Write-Portal "          .       +            .                 .                 .            +       ." "Cyan"
    Write-Portal "              [<]        >> NEXUS GRID                                  <|> SIGNAL LOCK        [>]" "Blue"
    Write-Host ""
    Write-Portal "Rule: models recommend; human authorizes durable mutation." "Blue"
    Write-Portal "Flow: portal -> surface -> evidence -> gate -> durable commit." "Cyan"
    Write-Host ""
    Write-Portal "  [1]  Open NexusGate                         -> full Electron operator HUD" "Cyan"
    Write-Portal "  [2]  Dev Mode / Handoff Console             -> patch / compiler / wound evidence" "Blue"
    Write-Portal "  [3]  Status / health surface                -> current health route" "Cyan"
    Write-Portal "  [4]  Terminal TUI surface                   -> terminal dashboard" "Cyan"
    Write-Portal "  [5]  NN router health                       -> local model readiness" "Cyan"
    Write-Portal "  [6]  Ask NEXUS router                       -> recommendation-only route" "Cyan"
    Write-Portal "  [7]  Open repo folder                       -> human inspection" "Cyan"
    Write-Portal "  [8]  Failure Modes / Doctor                 -> scan / classify / safe clean / retry" "Blue"
    Write-Portal "  [9]  GitHub / README / Docs                 -> repo links / entrypoints / changelog" "Cyan"
    Write-Portal "  [10] NexusCell / Containment                -> execution governance doctrine" "Blue"
    Write-Portal "  [11] NexusShell / Operator                  -> full-scope no-execution shell" "Blue"
    Write-Portal "  [12] NexusCell - Containment Cell / Gate    -> containment execution gate" "Blue"
    Write-Portal "  [13] Neural Activity / Cathedral            -> bioelectric popout HUD" "Cyan"
    Write-Portal "  [14] Nexus Loops / Cards                   -> JSON loop cards / HUD-ready registry" "Blue"
    Write-Portal "  [15] PetriDishPortal                       -> organism gate / microscope HUD" "Cyan"
    Write-Portal "  [16] T3MP3ST                               -> authorized security lab / War Room" "Blue"
    Write-Portal "  [17] Algorithm Cards                      -> predictive/control algorithms" "Cyan"
    Write-Portal "  [Q]  Quit" "Blue"
    Write-Host ""
    Write-Portal "========================================================================================================================" "Cyan"
    Write-Host ""
    # NEXUS_SPIRAL_CORE_ASCII_END

    # Compatibility markers for older static tests:
    # Write-Host "NEXUS GATE :: DESKTOP ENTRY PORTAL"
    # Write-Host "cyber ice-blue gateway for human + AI intelligence flow"
    # Write-Host "The gate does not give intelligence authority."
    # Write-Host "The gate gives authority a visible path through intelligence."
    # Write-Host "2. Dev Mode / Handoff Console"
    # Write-Host "[1] Open NexusGate"
    # Write-Host "[2] Dev Mode / Handoff Console"
    # Write-Host "[3] Status / health surface"
    # Write-Host "[4] Terminal TUI surface"
    # Write-Host "[5] NN router health"
    # Write-Host "[6] Ask NEXUS router"
    # Write-Host "[7] Open repo folder"
    # Write-Host "[8] Failure Modes / Doctor"
    # Write-Host "[9] GitHub / README / Docs"
    # Write-Host "[10] NexusCell / Containment"
    # Write-Host "[11] NexusShell / Operator"
    # Write-Host "[12] NexusCell - Containment Cell / Execution Gate"
    # Write-Host "[13] Neural Activity / Cathedral"
    # Write-Host "[14] Nexus Loops / Cards"
    # Write-Host "[15] PetriDishPortal"
    # Write-Host "[16] T3MP3ST"
    # Write-Host "[17] Algorithm Cards"
    # Write-Host "Gateway style: cyber ice-blue / green / yellow portal."
}

Write-NG "NEXUS Gate launcher opened."
Write-NG "Primary entry: Open NexusGate -> Electron UI."
Write-NG "Dev entry: Dev Mode / Handoff Console -> patch, compiler, wound evidence."
Write-NG "Gateway style: Spiral Core Portal / blue / light-blue."

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
    elseif ($choice -eq "8") {
        Invoke-NexusFailureModeDoctorConsole
    }
    elseif ($choice -eq "9") {
        Invoke-NexusResourceMenu
    }
    elseif ($choice -eq "10") {
        Invoke-NexusCellConsole
    }
    elseif ($choice -eq "12") {
        Invoke-NexusCellExecutionGateConsole
    }
    elseif ($choice -eq "11") {
        Invoke-NexusShellConsole
    }
    elseif ($choice -eq "13") {
        Invoke-NexusNeuralActivity
    }
    elseif ($choice -eq "14") {
        Invoke-NexusLoopCardsConsole
    }
    elseif ($choice -eq "15") {
        Invoke-NexusPetriDishPortal
    }
    elseif ($choice -eq "16") {
        Invoke-NexusT3mp3stPortal
    }
    elseif ($choice -eq "17") {
        Invoke-NexusAlgorithmCardsConsole
    }
    elseif ($choice -eq "Q" -or $choice -eq "q") {
        Write-OK "closing NEXUS Gate launcher"
        exit 0
    }
    else {
        Write-NG "Unknown choice."
    }
}
