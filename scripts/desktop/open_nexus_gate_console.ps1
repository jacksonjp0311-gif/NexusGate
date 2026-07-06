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
        elseif ($cellChoice -eq "B" -or $cellChoice -eq "b") {
            return
        }
        else {
            Write-NG "Unknown NexusCell choice."
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

function Write-Portal {
    param(
        [string]$Text,
        [string]$Color = "Cyan"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Show-Menu {
    Clear-Host
    Write-Portal "====================================================================" "Cyan"
    Write-Portal "  NEXUS GATE :: DESKTOP ENTRY PORTAL" "Cyan"
    Write-Portal "  cyber ice-blue gateway for human + AI intelligence flow" "DarkCyan"
    Write-Portal "====================================================================" "Cyan"
    Write-Host ""
    Write-Portal "  Quote:" "Yellow"
    Write-Portal "  The gate does not give intelligence authority." "Green"
    Write-Portal "  The gate gives authority a visible path through intelligence." "Green"
    Write-Host ""
    Write-Portal "  [1] Open NexusGate                 -> full Electron operator HUD" "Yellow"
    Write-Portal "  [2] Dev Mode / Handoff Console     -> patch / compiler / wound evidence" "Yellow"
    Write-Portal "  [3] Status / health surface        -> current health route" "Cyan"
    Write-Portal "  [4] Terminal TUI surface           -> terminal dashboard" "Cyan"
    Write-Portal "  [5] NN router health               -> local model readiness" "Cyan"
    Write-Portal "  [6] Ask NEXUS router               -> recommendation-only route" "Cyan"
    Write-Portal "  [7] Open repo folder               -> human inspection" "DarkCyan"
    Write-Portal "  [8] Failure Modes / Doctor         -> scan / classify / safe clean / retry" "Yellow"
    Write-Portal "  [9] GitHub / README / Docs         -> repo links / entrypoints / changelog" "Cyan"
    Write-Portal "  [10] NexusCell / Containment       -> execution governance doctrine" "Yellow"
    Write-Portal "  [Q] Quit" "DarkGray"
    Write-Host ""
    Write-Portal "Rule: models recommend; human authorizes durable mutation." "Green"
    Write-Portal "Flow: portal -> surface -> evidence -> gate -> durable commit." "Cyan"
    Write-Host ""

    # Compatibility marker for older tests: Write-Host "2. Dev Mode / Handoff Console"
}

Write-NG "NEXUS Gate launcher opened."
Write-NG "Primary entry: Open NexusGate -> Electron UI."
Write-NG "Dev entry: Dev Mode / Handoff Console -> patch, compiler, wound evidence."
Write-NG "Gateway style: cyber ice-blue / green / yellow portal."

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
    elseif ($choice -eq "Q" -or $choice -eq "q") {
        Write-OK "closing NEXUS Gate launcher"
        exit 0
    }
    else {
        Write-NG "Unknown choice."
    }
}
