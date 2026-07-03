# NEXUS GATE human-readable operator surface
# CRLF warning filter literals retained for tests and operator policy:
# CRLF will be replaced by LF
# LF will be replaced by CRLF
param(
    [ValidateSet("all", "compile", "runtime", "pack", "feedback", "interconnect", "compact", "heal", "interface", "evolve", "status", "gitfix")]
    [string]$Command = "all",
    [switch]$NoGit
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = "1"

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$HumanDir = Join-Path $Root "reports\human_surface\$Stamp"
[void](New-Item -ItemType Directory -Path $HumanDir -Force)

function Say {
    param([string]$Message, [string]$Level = "NG")
    Write-Host "[$Level] $Message"
}

function Write-Log {
    param([string]$Name, [string[]]$Lines)
    $Path = Join-Path $HumanDir $Name
    $Lines | Out-File -FilePath $Path -Encoding utf8
    return $Path
}

function Last-Lines {
    param([string[]]$Lines, [int]$Count = 30)
    if (-not $Lines) { return @() }
    if ($Lines.Count -le $Count) { return $Lines }
    return $Lines[($Lines.Count - $Count)..($Lines.Count - 1)]
}

function Invoke-Step {
    param(
        [string]$Name,
        [string]$LogName,
        [scriptblock]$Block,
        [switch]$AllowWarn
    )
    Say "$Name..."
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & $Block 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old
    $logPath = Write-Log -Name $LogName -Lines ($output | ForEach-Object { [string]$_ })

    if ($code -ne 0 -and -not $AllowWarn) {
        Say "$Name failed. Log: $logPath" "FAIL"
        Last-Lines -Lines ($output | ForEach-Object { [string]$_ }) -Count 60 | ForEach-Object { Write-Host $_ }
        exit $code
    }

    if ($code -ne 0 -and $AllowWarn) {
        Say "$Name warning routed. Log: $logPath" "WARN"
        return
    }

    Say "$Name passed. Log: $logPath" "OK"
}

function Set-GitQuietLineEndings {
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        git config core.autocrlf false | Out-Null
        git config core.safecrlf false | Out-Null
        git config core.eol native | Out-Null
    }
}

function Show-FeedbackSummary {
    $path = ".\reports\nexus_feedback_interface_report_latest.json"
    if (Test-Path $path) {
        try {
            $data = Get-Content $path -Raw | ConvertFrom-Json
            Say "Feedback summary" "NG"
            Say "Health score: $($data.health_score)" "OK"
            Say "Evidence pressure: $($data.evidence_pressure)" "OK"
            Say "Dominant pressure: $($data.dominant_pressure_source)" "OK"
            Say "Next action: $($data.next_action)" "OK"
            Say "AI context: $($data.ai_context_path)" "OK"
            Say "Feedback log: $($data.markdown_log_path)" "OK"
        }
        catch {
            Say "Feedback summary unavailable; report unreadable." "WARN"
        }
    } else {
        Say "Feedback interface report missing." "WARN"
    }
}

function Run-Compile {
    Say "NEXUS GATE human compile surface"
    Say "Detailed logs: $HumanDir"
    Invoke-Step "Python compile" "01_python_compile.log" { python -m compileall nexus_gate tests }
    Invoke-Step "Unit tests" "02_unit_tests.log" { python -m unittest discover -s tests }
    Invoke-Step "NEXUS compiler" "03_nexus_compiler.json" { python -m nexus_gate.compiler --root . --json }
    Invoke-Step "Adapter compiler" "04_adapter_compiler.json" { python -m nexus_gate.adapters.compile --root . --json }
    Invoke-Step "Receptor compiler" "05_receptor_compiler.json" { python -m nexus_gate.receptors.compile --root . --json }
    Invoke-Step "Bridge compiler" "06_bridge_compiler.json" { python -m nexus_gate.bridge.compile --root . --json }
    Invoke-Step "Runtime compiler" "07_runtime_compiler.json" { python -m nexus_gate.bridge.runtime_compiler --root . --json }
    Say "Compile lanes passed." "OK"
}

function Run-Feedback {
    Invoke-Step "Evidence compaction" "08_evidence_compaction.json" { python -m nexus_gate.evidence.compact --root . --json }
    Invoke-Step "Interconnect compiler" "09_interconnect_compiler.json" { python -m nexus_gate.interconnect.compile --root . --json }
    Invoke-Step "Feedback compiler" "10_feedback_compiler.json" { python -m nexus_gate.feedback.compile --root . --json }
    Invoke-Step "Self-healing compiler" "11_self_healing_compiler.json" { python -m nexus_gate.self_healing.compile --root . --json } -AllowWarn
    Invoke-Step "AI feedback interface" "12_ai_feedback_interface.json" { python -m nexus_gate.feedback.interface_compile --root . --json }
    Say "Feedback/self-healing/interface lanes passed." "OK"
    Show-FeedbackSummary
}

function Run-Pack {
    Invoke-Step "Pack compiler" "13_pack_compiler.json" { python -m nexus_gate.build.packer --root . --out dist --json }
    Say "Pack lane passed." "OK"
}

function Run-All {
    Run-Compile
    Run-Feedback
    Run-Pack
    Say "Compiled report files written." "OK"
    Say "Human surface passed." "OK"
}

function Show-Status {
    Say "NEXUS GATE status"
    foreach ($path in @(
        ".\reports\nexus_compile_report_latest.json",
        ".\reports\nexus_adapter_compile_report_latest.json",
        ".\reports\nexus_receptor_compile_report_latest.json",
        ".\reports\nexus_bridge_compile_report_latest.json",
        ".\reports\nexus_runtime_compile_report_latest.json",
        ".\reports\nexus_bounded_runtime_report_latest.json",
        ".\reports\nexus_evidence_compaction_report_latest.json",
        ".\reports\nexus_interconnect_report_latest.json",
        ".\reports\nexus_feedback_report_latest.json",
        ".\reports\nexus_self_healing_report_latest.json",
        ".\reports\nexus_feedback_interface_report_latest.json",
        ".\state\ai_feedback_context_latest.json",
        ".\docs\feedback\FEEDBACK_LOG.md",
        ".\dist\nexus_gate_pack_manifest_latest.json"
    )) {
        if (Test-Path $path) {
            try {
                $data = Get-Content $path -Raw | ConvertFrom-Json
                $status = $data.status
                if (-not $status) { $status = "present" }
                Say "$path => $status" "OK"
            }
            catch {
                Say "$path => present" "OK"
            }
        }
        if (-not (Test-Path $path)) {
            Say "$path => missing" "WARN"
        }
    }
    Show-FeedbackSummary
}

if ($Command -eq "gitfix") {
    Set-GitQuietLineEndings
    Say "Local Git line-ending noise policy applied." "OK"
    exit 0
}

if ($Command -eq "status") {
    Show-Status
    exit 0
}

if ($Command -eq "compile") {
    Run-Compile
    exit 0
}

if ($Command -eq "runtime") {
    Invoke-Step "Runtime compiler" "07_runtime_compiler.json" { python -m nexus_gate.bridge.runtime_compiler --root . --json }
    Say "Runtime surface passed." "OK"
    exit 0
}

if ($Command -eq "compact") {
    Invoke-Step "Evidence compaction" "08_evidence_compaction.json" { python -m nexus_gate.evidence.compact --root . --json }
    Say "Evidence compaction passed." "OK"
    exit 0
}

if ($Command -eq "interconnect") {
    Invoke-Step "Interconnect compiler" "09_interconnect_compiler.json" { python -m nexus_gate.interconnect.compile --root . --json }
    Say "Interconnect passed." "OK"
    exit 0
}

if ($Command -eq "feedback") {
    Run-Feedback
    exit 0
}

if ($Command -eq "heal") {
    Invoke-Step "Self-healing compiler" "11_self_healing_compiler.json" { python -m nexus_gate.self_healing.compile --root . --json } -AllowWarn
    Invoke-Step "AI feedback interface" "12_ai_feedback_interface.json" { python -m nexus_gate.feedback.interface_compile --root . --json }
    Say "Self-healing feedback report written." "OK"
    Show-FeedbackSummary
    exit 0
}

if ($Command -eq "interface") {
    Invoke-Step "AI feedback interface" "12_ai_feedback_interface.json" { python -m nexus_gate.feedback.interface_compile --root . --json }
    Show-FeedbackSummary
    exit 0
}

if ($Command -eq "pack") {
    Run-Pack
    exit 0
}

if ($Command -eq "evolve") {
    Run-All
    exit 0
}

Run-All
