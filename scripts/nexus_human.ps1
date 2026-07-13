# NEXUS GATE human-readable operator surface
# CRLF warning filter literals retained for tests and operator policy:
# CRLF will be replaced by LF
# LF will be replaced by CRLF
param(
    [ValidateSet("all", "compile", "runtime", "pack", "feedback", "interconnect", "compact", "heal", "interface", "electron-env", "electron-preflight", "reflect", "domain", "meta-orchestrator", "orchestrate", "predictive-timing", "predictive-memory", "epoch-seal", "epoch-verify", "epoch-chain-verify", "epoch-observe", "origin-seal", "triadic-lattice", "distill", "decision-envelope", "coherence-field", "outcome-learn", "runtime-hygiene", "clean-runtime", "action-recommend", "action-chain-verify", "action-semantic-verify", "experience-readiness", "experience-chain-verify", "calibration-replay-verify", "adaptive-coherence", "emergence-report", "causal-receipts", "first-learning-readiness", "evolve", "status", "gitfix")]
    [string]$Command = "all",
    [string]$ActionId = "",
    [switch]$NoGit
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = "1"
$StepTimeoutSeconds = 180
if ($env:NEXUS_HUMAN_STEP_TIMEOUT_SECONDS) {
    try {
        $parsedTimeout = [int]$env:NEXUS_HUMAN_STEP_TIMEOUT_SECONDS
        if ($parsedTimeout -gt 0) { $StepTimeoutSeconds = $parsedTimeout }
    }
    catch {
        $StepTimeoutSeconds = 180
    }
}

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
        [switch]$AllowWarn,
        [int]$TimeoutSeconds = $StepTimeoutSeconds
    )
    Say "$Name... timeout=${TimeoutSeconds}s"
    $encodedBlock = $Block.ToString()
    $job = Start-Job -ScriptBlock {
        param([string]$JobRoot, [string]$JobBlock)
        Set-Location $JobRoot
        $env:PYTHONUTF8 = "1"
        $ErrorActionPreference = "Continue"
        $global:LASTEXITCODE = 0
        try {
            $script = [scriptblock]::Create($JobBlock)
            & $script 2>&1
            $code = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
        }
        catch {
            Write-Output $_
            $code = 1
        }
        Write-Output ("[[NEXUS_EXIT_CODE:{0}]]" -f $code)
    } -ArgumentList $Root, $encodedBlock

    $completed = Wait-Job -Job $job -Timeout $TimeoutSeconds
    if (-not $completed) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue | Out-Null
        $output = @("NEXUS step timeout after ${TimeoutSeconds}s.")
        $code = 124
        Remove-Job -Job $job -Force | Out-Null
    }
    else {
        $rawOutput = @(Receive-Job -Job $job 2>&1)
        Remove-Job -Job $job -Force | Out-Null
        $marker = $rawOutput | Where-Object { [string]$_ -match '^\[\[NEXUS_EXIT_CODE:\d+\]\]$' } | Select-Object -Last 1
        if ($marker) {
            $code = [int](([string]$marker) -replace '^\[\[NEXUS_EXIT_CODE:(\d+)\]\]$', '$1')
            $output = @($rawOutput | Where-Object { [string]$_ -notmatch '^\[\[NEXUS_EXIT_CODE:\d+\]\]$' })
        }
        else {
            $code = 1
            $output = @($rawOutput + "NEXUS step did not emit an exit-code marker.")
        }
    }
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
    Invoke-Step "Electron environment gate" "13_electron_environment.json" { python -m nexus_gate.ui.electron_environment_compile --root . --json }
    Invoke-Step "Electron preflight compiler" "14_electron_preflight.json" { python -m nexus_gate.ui.electron_preflight_compile --root . --json }
    Invoke-Step "Reflective loop compiler" "15_reflective_loop.json" { python -m nexus_gate.reflection.compile --root . --json }
    Invoke-Step "Domain intelligence compiler" "16_domain_intelligence.json" { python -m nexus_gate.domain.compile --root . --json }
    Invoke-Step "Meta-orchestrator gate" "16b_meta_orchestrator_gate.json" { python -m nexus_gate.loops.meta_orchestrator_gate --root . --intent "evolve chain meta-orchestrator seal" --json }
    Invoke-Step "Loop orchestrator" "16c_loop_orchestrator.json" { python -m nexus_gate.loops.orchestrator --root . --intent "evolve chain loop orchestration plan" --json }
    Invoke-Step "Predictive timing" "16d_predictive_timing.json" { python -m nexus_gate.loops.predictive_timing --root . --json }
    Invoke-Step "Predictive memory orchestrator" "16e_predictive_memory_orchestrator.json" { python -m nexus_gate.loops.predictive_memory_orchestrator --root . --intent "evolve chain Cortex memory and predictive gate fusion" --json }
    Invoke-Step "Epoch integrity seal" "16e2_epoch_integrity_seal.json" { python -m nexus_gate.epochs.seal --root . --json }
    Invoke-Step "Epoch integrity verify" "16e3_epoch_integrity_verify.json" { python -m nexus_gate.epochs.seal --root . --verify --json }
    Invoke-Step "Origin seal" "16f_origin_seal.json" { python -m nexus_gate.origin.seal --root . --json }
    Invoke-Step "Triadic geometric lattice" "16f2_triadic_lattice.json" { python -m nexus_gate.lattice.triadic --root . --json }
    Invoke-Step "Decision envelope" "16g_decision_envelope.json" { python -m nexus_gate.decision.envelope --root . --intent "evolve chain self-bootstrap decision envelope" --json }
    Invoke-Step "Coherence field" "16h_coherence_field.json" { python -m nexus_gate.coherence.field --root . --intent "evolve chain coherence continuity field" --json }
    Invoke-Step "Outcome learner" "16i_outcome_learner.json" { python -m nexus_gate.outcomes.learn --root . --intent "evolve chain recommendation outcome learning" --json }
    Invoke-Step "Evidence distillation graph" "16i2_evidence_distillation.json" { python -m nexus_gate.distillation.graph --root . --json }
    Invoke-Step "Causal action recommendation shadow receipt" "16i3_causal_action_recommendation.json" { python -m nexus_gate.actions.cli recommend --root . --json }
    Invoke-Step "Causal action chain verify" "16i4_action_chain_verify.json" { python -m nexus_gate.actions.cli chain-verify --root . --json }
    Say "Feedback/self-healing/interface lanes passed." "OK"
    Show-FeedbackSummary
}

function Run-Pack {
    Invoke-Step "Pack compiler" "17_pack_compiler.json" { python -m nexus_gate.build.packer --root . --out dist --json } -TimeoutSeconds ([Math]::Max($StepTimeoutSeconds, 420))
    Say "Pack lane passed." "OK"
}

function Run-All {
    Run-Compile
    Run-Feedback
    Run-Pack
    Invoke-Step "Runtime hygiene" "18_runtime_hygiene.json" { python -m nexus_gate.hygiene.runtime_churn --root . --json }
    Invoke-Step "First learning readiness" "18b_first_learning_readiness.json" { python -m nexus_gate.actions.cli first-learning-readiness --root . --json }
    Invoke-Step "Action semantic verify" "18c_action_semantic_verify.json" { python -m nexus_gate.actions.cli semantic-verify --root . --json }
    Invoke-Step "Experience chain verify" "18d_experience_chain_verify.json" { python -m nexus_gate.actions.cli experience-chain-verify --root . --json }
    Invoke-Step "Calibration replay verify" "18e_calibration_replay_verify.json" { python -m nexus_gate.actions.cli calibration-replay-verify --root . --json }
    Invoke-Step "Adaptive coherence" "18f_adaptive_coherence.json" { python -m nexus_gate.actions.cli adaptive-coherence --root . --json }
    Invoke-Step "Emergence observation" "18g_emergence_observation.json" { python -m nexus_gate.actions.cli emergence-report --root . --json }
    Invoke-Step "Epoch chain verify" "19_epoch_chain_verify.json" { python -m nexus_gate.epochs.seal --root . --chain-verify --json }
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
        ".\reports\nexus_electron_environment_report_latest.json",
        ".\reports\nexus_electron_preflight_report_latest.json",
        ".\reports\nexus_reflective_loop_report_latest.json",
        ".\reports\nexus_domain_intelligence_report_latest.json",
        ".\reports\nexus_meta_orchestrator_gate_latest.json",
        ".\reports\nexus_loop_orchestration_report_latest.json",
        ".\reports\nexus_predictive_memory_orchestrator_latest.json",
        ".\reports\nexus_epoch_integrity_seal_latest.json",
        ".\reports\nexus_origin_seal_latest.json",
        ".\reports\nexus_triadic_lattice_latest.json",
        ".\reports\nexus_decision_envelope_latest.json",
        ".\reports\nexus_coherence_field_latest.json",
        ".\reports\nexus_recommendation_outcome_latest.json",
        ".\reports\nexus_evidence_distillation_report_latest.json",
        ".\reports\nexus_runtime_hygiene_latest.json",
        ".\state\nexus_origin_manifest_latest.json",
        ".\state\lattice\nexus_triadic_lattice_latest.json",
        ".\state\decision\nexus_decision_envelope_latest.json",
        ".\state\coherence\nexus_coherence_field_latest.json",
        ".\state\distillation\nexus_evidence_graph_latest.json",
        ".\state\latest_epoch_pointer.json",
        ".\state\coherence\arbiter_calibration_latest.json",
        ".\state\coherence\pressure_memory_latest.json",
        ".\state\nexus_lineage_manifest_latest.json",
        ".\state\interface_adapter_contract_index.v0.3.7.json",
        ".\state\domain_intelligence_index.v0.4.0.json",
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

if ($Command -eq "electron-env") {
    Invoke-Step "Electron environment gate" "13_electron_environment.json" { python -m nexus_gate.ui.electron_environment_compile --root . --json }
    Say "Electron environment report written." "OK"
    exit 0
}

if ($Command -eq "electron-preflight") {
    Invoke-Step "Electron preflight compiler" "14_electron_preflight.json" { python -m nexus_gate.ui.electron_preflight_compile --root . --json }
    Say "Electron preflight report written." "OK"
    exit 0
}

if ($Command -eq "reflect") {
    Invoke-Step "Reflective loop compiler" "15_reflective_loop.json" { python -m nexus_gate.reflection.compile --root . --json }
    Say "Reflective loop report written." "OK"
    exit 0
}

if ($Command -eq "domain") {
    Invoke-Step "Domain intelligence compiler" "16_domain_intelligence.json" { python -m nexus_gate.domain.compile --root . --json }
    Say "Domain intelligence report written." "OK"
    exit 0
}

if ($Command -eq "meta-orchestrator") {
    Invoke-Step "Meta-orchestrator gate" "16b_meta_orchestrator_gate.json" { python -m nexus_gate.loops.meta_orchestrator_gate --root . --intent "human surface meta-orchestrator gate" --json }
    Say "Meta-orchestrator report written." "OK"
    exit 0
}

if ($Command -eq "orchestrate") {
    Invoke-Step "Loop orchestrator" "16c_loop_orchestrator.json" { python -m nexus_gate.loops.orchestrator --root . --intent "human surface loop orchestration plan" --json }
    Say "Loop orchestration report written." "OK"
    exit 0
}

if ($Command -eq "predictive-timing") {
    Invoke-Step "Predictive timing" "16d_predictive_timing.json" { python -m nexus_gate.loops.predictive_timing --root . --json }
    Say "Predictive timing report written." "OK"
    exit 0
}

if ($Command -eq "predictive-memory") {
    Invoke-Step "Predictive memory orchestrator" "16e_predictive_memory_orchestrator.json" { python -m nexus_gate.loops.predictive_memory_orchestrator --root . --intent "human surface Cortex memory and predictive gate fusion" --json }
    Say "Predictive memory report written." "OK"
    exit 0
}

if ($Command -eq "origin-seal") {
    Invoke-Step "Origin seal" "16f_origin_seal.json" { python -m nexus_gate.origin.seal --root . --json }
    Say "Origin seal report written." "OK"
    exit 0
}

if ($Command -eq "epoch-seal") {
    Invoke-Step "Epoch integrity seal" "16e2_epoch_integrity_seal.json" { python -m nexus_gate.epochs.seal --root . --json }
    Say "Epoch integrity seal report written." "OK"
    exit 0
}

if ($Command -eq "epoch-observe") {
    Invoke-Step "Epoch observation" "16e2_epoch_integrity_seal.json" { python -m nexus_gate.epochs.seal --root . --json }
    Say "Epoch observation written." "OK"
    exit 0
}

if ($Command -eq "epoch-verify") {
    Invoke-Step "Epoch integrity verify" "16e3_epoch_integrity_verify.json" { python -m nexus_gate.epochs.seal --root . --verify --json }
    Say "Epoch integrity verified." "OK"
    exit 0
}

if ($Command -eq "epoch-chain-verify") {
    Invoke-Step "Epoch chain verify" "16e4_epoch_chain_verify.json" { python -m nexus_gate.epochs.seal --root . --chain-verify --json }
    Say "Epoch chain verified." "OK"
    exit 0
}

if ($Command -eq "triadic-lattice") {
    Invoke-Step "Triadic geometric lattice" "16f2_triadic_lattice.json" { python -m nexus_gate.lattice.triadic --root . --json }
    Say "Triadic lattice report written." "OK"
    exit 0
}

if ($Command -eq "decision-envelope") {
    Invoke-Step "Decision envelope" "16g_decision_envelope.json" { python -m nexus_gate.decision.envelope --root . --intent "human surface self-bootstrap decision envelope" --json }
    Say "Decision envelope report written." "OK"
    exit 0
}

if ($Command -eq "coherence-field") {
    Invoke-Step "Coherence field" "16h_coherence_field.json" { python -m nexus_gate.coherence.field --root . --intent "human surface coherence continuity field" --json }
    Say "Coherence field report written." "OK"
    exit 0
}

if ($Command -eq "outcome-learn") {
    Invoke-Step "Outcome learner" "16i_outcome_learner.json" { python -m nexus_gate.outcomes.learn --root . --intent "human surface recommendation outcome learning" --json }
    Say "Outcome learner report written." "OK"
    exit 0
}

if ($Command -eq "distill") {
    Invoke-Step "Evidence distillation graph" "16i2_evidence_distillation.json" { python -m nexus_gate.distillation.graph --root . --json }
    Say "Evidence distillation graph written." "OK"
    exit 0
}

if ($Command -eq "runtime-hygiene") {
    Invoke-Step "Runtime hygiene" "16j_runtime_hygiene.json" { python -m nexus_gate.hygiene.runtime_churn --root . --json }
    Say "Runtime hygiene report written." "OK"
    exit 0
}

if ($Command -eq "action-recommend") {
    Invoke-Step "Causal action recommendation" "16i3_causal_action_recommendation.json" { python -m nexus_gate.actions.cli recommend --root . --json }
    Say "Causal action recommendation receipt written." "OK"
    exit 0
}

if ($Command -eq "action-chain-verify") {
    Invoke-Step "Causal action chain verify" "16i4_action_chain_verify.json" { python -m nexus_gate.actions.cli chain-verify --root . --json }
    Say "Causal action chain verified." "OK"
    exit 0
}

if ($Command -eq "action-semantic-verify") {
    Invoke-Step "Causal action semantic verify" "16i4b_action_semantic_verify.json" {
        if ([string]::IsNullOrWhiteSpace($ActionId)) { python -m nexus_gate.actions.cli semantic-verify --root . --json }
        else { python -m nexus_gate.actions.cli semantic-verify --root . --action-id $ActionId --json }
    }
    Say "Causal action semantics verified." "OK"
    exit 0
}

if ($Command -eq "experience-readiness") {
    Invoke-Step "Experience readiness" "16i6_experience_readiness.json" { python -m nexus_gate.actions.cli experience-readiness --root . --json }
    Say "Experience readiness report written." "OK"
    exit 0
}

if ($Command -eq "experience-chain-verify") {
    Invoke-Step "Experience chain verify" "16i7_experience_chain_verify.json" { python -m nexus_gate.actions.cli experience-chain-verify --root . --json }
    Say "Experience chain verified." "OK"
    exit 0
}

if ($Command -eq "calibration-replay-verify") {
    Invoke-Step "Calibration replay verify" "16i8_calibration_replay_verify.json" { python -m nexus_gate.actions.cli calibration-replay-verify --root . --json }
    Say "Calibration replay verified." "OK"
    exit 0
}

if ($Command -eq "adaptive-coherence") {
    Invoke-Step "Adaptive coherence" "16i9_adaptive_coherence.json" { python -m nexus_gate.actions.cli adaptive-coherence --root . --json }
    Say "Adaptive coherence report written." "OK"
    exit 0
}

if ($Command -eq "emergence-report") {
    Invoke-Step "Emergence observation" "16i10_emergence_observation.json" { python -m nexus_gate.actions.cli emergence-report --root . --json }
    Say "Emergence observation report written." "OK"
    exit 0
}

if ($Command -eq "causal-receipts") {
    Invoke-Step "Causal action status" "16i5_causal_action_status.json" { python -m nexus_gate.actions.cli receipts --root . --action-id $ActionId --json }
    Say "Causal action status written." "OK"
    exit 0
}

if ($Command -eq "first-learning-readiness") {
    Invoke-Step "First learning readiness" "16i6_first_learning_readiness.json" { python -m nexus_gate.actions.cli first-learning-readiness --root . --json }
    Say "First learning readiness report written." "OK"
    exit 0
}

if ($Command -eq "clean-runtime") {
    Invoke-Step "Runtime hygiene clean" "16j_runtime_hygiene.json" { python -m nexus_gate.hygiene.runtime_churn --root . --apply --json }
    Say "Runtime generated churn cleaned." "OK"
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
