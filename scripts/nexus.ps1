# NEXUS GATE compact PowerShell command surface
# Legacy direct compiler markers retained for audit/tests:
# nexus_gate.adapters.compile
# nexus_gate.receptors.compile
# nexus_gate.bridge.compile
# nexus_gate.bridge.runtime_compiler
# nexus_gate.feedback.compile
# nexus_gate.feedback.interface_compile
# nexus_gate.interconnect.compile
# nexus_gate.evidence.compact
# nexus_gate.self_healing.compile
# nexus_gate.reflection.compile
# nexus_gate.domain.compile
# nexus_gate.loops.predictive_timing
# nexus_gate.loops.predictive_evolve
# nexus_gate.loops.predictive_memory_orchestrator
# nexus_gate.loops.certificate_resume
# nexus_gate.origin.seal
# nexus_gate.hygiene.runtime_churn
# nexus_gate.algorithms.cards
# nexus_gate.discoveries.cards
# nexus_gate.lattice.triadic
# nexus_gate.distillation.graph
# nexus_gate.epochs.seal
# nexus_gate.actions.cli
param(
    [ValidateSet("rehydrate", "compile", "strict", "pack", "adapters", "receptors", "bridge", "runtime", "human", "feedback", "interconnect", "compact", "heal", "interface", "electron-env", "electron-preflight", "reflect", "domain", "tui", "ui", "evolve", "once", "loop", "watch", "status", "promote", "nn", "nn-health", "tnn","tnn-chat", "ask", "fast", "balanced", "deep", "align-score", "geo", "geo-clean", "cell-plan", "cell-context", "shell", "cell-bridge", "cell-run", "cell", "cell-doctor", "cell-ledger", "cell-policy","tnn-health","tnn-warm","tnn-deep","tnn-doctor", "meta-loop", "meta-orchestrator", "orchestrate", "predictive-timing", "predictive-evolve", "predictive-memory", "certificate-resume", "epoch-seal", "epoch-verify", "epoch-chain-verify", "epoch-observe", "origin-seal", "triadic-lattice", "distill", "decision-envelope", "coherence-field", "outcome-learn", "runtime-hygiene", "clean-runtime", "action-recommend", "action-status", "action-authorize", "action-deny", "action-execute", "action-effects", "action-final-evolve", "action-validate", "action-finalize", "action-chain-verify", "action-semantic-verify", "experience-readiness", "experience-seal", "experience-chain-verify", "calibration-status", "calibration-authorize", "calibration-apply", "calibration-replay-verify", "adaptive-coherence", "emergence-report", "causal-receipts", "first-learning-readiness", "install-hooks", "algorithm-cards", "discovery-cards", "loops", "loop-registry", "phi-gate", "phi-gate-auto", "phi-gate-compile", "phi-loop", "phi-loop-auto", "phi-wound", "phi-wound-gpu", "toolbelt", "toolbelt-start", "toolbelt-dashboard", "toolbelt-next", "toolbelt-ship", "toolbelt-json", "wound-compress", "preflight", "preflight-json", "cortex", "cortex-refresh", "sync-cortex")]
    [string]$Command = "rehydrate",
    [int]$Cycles = 1,
    [int]$Interval = 5,
    [string]$Tag = "",
    [string]$ActionId = "",
    [switch]$NoCommit,
    [switch]$CallModel,
    [string]$Loop = "rhp-core",
    [string]$Gate = "ci-core",
    [switch]$Execute,
    [switch]$HumanAuthorized
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Run-Compiler {
    python -m nexus_gate.compiler --root . --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS GATE compiler failed." }
}

function Show-Rehydration {
    Write-Host "[NG] Rehydration visibility"
    foreach ($path in @(
        ".\docs\goal\GOAL_LOCK.md",
        ".\docs\adapters\ADAPTER_REGISTRY.md",
        ".\docs\receptors\RECEPTOR_REGISTRY.md",
        ".\docs\bridge\BRIDGE_SESSION_RUNNER.md",
        ".\docs\bridge\BOUNDED_BRIDGE_RUNTIME.md",
        ".\docs\runtime\HUMAN_SURFACE.md",
        ".\docs\runtime\FEEDBACK_INTERCONNECT.md",
        ".\docs\runtime\SELF_HEALING_FEEDBACK.md",
        ".\docs\feedback\FEEDBACK_SYSTEM.md",
        ".\docs\feedback\FEEDBACK_LOG.md",
        ".\docs\ui\NEXUS_TUI_SHELL.md",
        ".\docs\intelligence\REFLECTIVE_INTELLIGENCE_LOOP.md",
        ".\docs\intelligence\DOMAIN_INTELLIGENCE_ORCHESTRATOR.md",
        ".\docs\intelligence\REPO_NATIVE_LEARNING.md",
        ".\docs\intelligence\CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md",
        ".\docs\codex\CODEX_ORCHESTRATION_PROTOCOL.md",
        ".\docs\interfaces\INTERFACE_ADAPTER_CONTRACT.md",
        ".\docs\versioning\NEXUS_LINEAGE_PROTOCOL.md",
        ".\docs\failure_modes\FAILURE_MODE_CHART.md",
        ".\docs\updates\UPDATE_CHART.md"
    )) {
        if (Test-Path $path) { Get-Content $path -TotalCount 80 }
    }
    if (Test-Path .\state\ai_feedback_context_latest.json) { Get-Content .\state\ai_feedback_context_latest.json -Raw }
    if (Test-Path .\reports\nexus_compile_report_latest.json) { Get-Content .\reports\nexus_compile_report_latest.json -Raw }
}

function Run-Loop {
    param([int]$MaxCycles, [int]$SleepSeconds, [switch]$Forever)
    $i = 0
    while ($true) {
        $i += 1
        Write-Host "[NG] Cycle $i"
        powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve
        if ($LASTEXITCODE -ne 0) { throw "NEXUS human/evolve failed." }
        if (-not $Forever -and $i -ge $MaxCycles) { break }
        Start-Sleep -Seconds $SleepSeconds
    }
}

function Show-Status {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 status
}

function Promote {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd -and -not $NoCommit) {
        git config core.autocrlf false | Out-Null
        git config core.safecrlf false | Out-Null
        git add . 2>$null | Out-Host
        $status = git status --porcelain
        if ($status) { git commit -m "chore: promote NEXUS GATE TUI pass" | Out-Host }
    }
    if ($gitCmd -and $Tag -ne "") { git tag $Tag | Out-Host }
    Write-Host "[OK] Promotion gate passed."
}

function Invoke-NexusGeo {
    param([string]$Intent = "What should we do next?")
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "What should we do next?"
    }
    python -m nexus_gate.geometric_memory.router --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS geometric memory packet compile failed." }
}

function Invoke-NexusGeoClean {
    python -m nexus_gate.geometric_memory.cleanup --root . --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS geometric cleanup failed." }
}


function Invoke-NexusMetaLoop {
    param(
        [string]$LoopName = "rhp-core",
        [string]$Intent = "Nexus meta loop trigger.",
        [switch]$Run,
        [switch]$Authorized
    )
    if ([string]::IsNullOrWhiteSpace($LoopName)) {
        $LoopName = "rhp-core"
    }
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "Nexus meta loop trigger."
    }
    $args = @("-m", "nexus_gate.loops.runner", "--root", ".", "--loop", $LoopName, "--intent", $Intent)
    if ($Run.IsPresent) {
        $args += "--execute"
    }
    if ($Authorized.IsPresent) {
        $args += "--human-authorized"
    }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS meta loop failed." }
}

function Show-NexusLoopRegistry {
    if (Test-Path .\loops\nexus_loop_registry.v0.1.json) {
        python -m nexus_gate.loops.runner --root . --list
    }
    if (-not (Test-Path .\loops\nexus_loop_registry.v0.1.json)) {
        throw "Loop registry missing."
    }
}
function Invoke-NexusNN {
    param(
        [string]$Intent = "What should we do next?",
        [string]$Role = "ALL",
        [switch]$UseModel
    )

    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "What should we do next?"
    }

    $args = @("-m", "nexus_gate.nn_router.compile", "--root", ".", "--intent", $Intent, "--role", $Role)
    if ($UseModel.IsPresent) {
        $args += "--call-model"
    }

    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS NN router compile failed." }
}
function Invoke-NexusCellPlan {
    param([string]$Intent = "Plan a gated NexusCell invocation.")
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "Plan a gated NexusCell invocation."
    }
    python -m nexus_gate.nexus_cell.plan --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NexusCell read-only planner failed." }
}

function Invoke-NexusCellContext {
    param([string]$Intent = "Build a bounded NexusCell context bridge.")
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "Build a bounded NexusCell context bridge."
    }
    python -m nexus_gate.nexus_cell.context_bridge --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NexusCell context bridge failed." }
}

function Invoke-NexusShell {
    param([string]$Intent = "Inspect NexusGate status.", [string]$ShellCommand = "status")
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "Inspect NexusGate status."
    }
    python -m nexus_gate.nexus_shell.shell --root . --command $ShellCommand --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NexusShell operator packet failed." }
}

function Invoke-NexusCellBridge {
    param([string]$Intent = "Build a NexusCell core bridge packet.")
    if ([string]::IsNullOrWhiteSpace($Intent)) {
        $Intent = "Build a NexusCell core bridge packet."
    }
    python -m nexus_gate.nexus_cell.bridge --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NexusCell core bridge failed." }
}

function Invoke-NexusCellRun {
    param([string]$Lane = "cell-bridge")
    if ([string]::IsNullOrWhiteSpace($Lane)) {
        $Lane = "cell-bridge"
    }
    python -m nexus_gate.nexus_cell.run --root . --lane $Lane --intent ("NexusCell controlled lane: " + $Lane) --json
    if ($LASTEXITCODE -ne 0) { throw "NexusCell full core run packet failed." }
}

function Invoke-NexusCellDoctorCli {
    python -m nexus_gate.nexus_cell.cli doctor --root .
    if ($LASTEXITCODE -ne 0) { throw "NexusCell doctor failed." }
}

function Invoke-NexusCellRunCli {
    python -m nexus_gate.nexus_cell.cli run --root . --runner mock --payload ".\NexusCell\examples\hello.ps1"
    if ($LASTEXITCODE -ne 0) { throw "NexusCell mock run failed." }
}

function Invoke-NexusCellLedgerCli {
    python -m nexus_gate.nexus_cell.cli ledger --root .
    if ($LASTEXITCODE -ne 0) { throw "NexusCell ledger failed." }
}

function Invoke-NexusCellPolicyCli {
    python -m nexus_gate.nexus_cell.cli policy --root .
    if ($LASTEXITCODE -ne 0) { throw "NexusCell policy failed." }
}




function Invoke-NexusPreflightOptimizer {
    param([string]$Intent = "Preflight next Nexus mutation surface.", [switch]$Json)
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Preflight next Nexus mutation surface." }
    $args = @("-m", "nexus_gate.loops.preflight_optimizer", "--root", ".", "--intent", $Intent)
    if ($Json.IsPresent) { $args += "--json" }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS preflight optimizer failed." }
}

function Invoke-NexusWoundCompression {
    param([string]$Intent = "Compress active Nexus wound.")
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Compress active Nexus wound." }
    python -m nexus_gate.loops.wound_compression --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS wound compression failed." }
}




function Invoke-NexusPhiGateSupervisor {
    param(
        [string]$Intent = "Run Phi Gate Supervisor.",
        [string]$GateName = "ci-core",
        [switch]$Auto
    )
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Run Phi Gate Supervisor." }
    if ([string]::IsNullOrWhiteSpace($GateName)) { $GateName = "ci-core" }
    $env:NEXUS_PHI4_MINI_COMMAND = 'python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    $args = @("-m", "nexus_gate.loops.phi_gate_supervisor", "--root", ".", "--intent", $Intent, "--gate", $GateName, "--call-model")
    if ($Auto.IsPresent) {
        $args += "--auto-repair"
        $args += "--human-authorized"
    }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Phi Gate Supervisor failed." }
}

function Invoke-NexusPhiGateCompile {
    python -m nexus_gate.loops.phi_gate_supervisor_compile --root . --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Phi Gate Supervisor compiler failed." }
}

function Invoke-NexusMetaOrchestratorGate {
    param([string]$Intent = "Compile the NEXUS meta-orchestrator gate.")
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Compile the NEXUS meta-orchestrator gate." }
    python -m nexus_gate.loops.meta_orchestrator_gate --root . --intent $Intent --json
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Meta-Orchestrator Gate failed." }
}

function Invoke-NexusLoopOrchestrator {
    param(
        [string]$Intent = "Orchestrate the next NEXUS loop.",
        [switch]$Run,
        [switch]$Authorized
    )
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Orchestrate the next NEXUS loop." }
    $args = @("-m", "nexus_gate.loops.orchestrator", "--root", ".", "--intent", $Intent, "--json")
    if ($Run.IsPresent) { $args += "--execute" }
    if ($Authorized.IsPresent) { $args += "--human-authorized" }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Loop Orchestrator failed." }
}

function Invoke-NexusPhiMicrodoseLoop {
    param(
        [string]$Intent = "Run bounded Phi microdose loop.",
        [switch]$Auto
    )
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Run bounded Phi microdose loop." }
    $env:NEXUS_PHI4_MINI_COMMAND = 'python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    $args = @("-m", "nexus_gate.loops.phi_microdose_loop", "--root", ".", "--intent", $Intent, "--call-model")
    if ($Auto.IsPresent) { $args += "--run-gates" }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Phi Microdose Loop failed." }
}

function Invoke-NexusPhiWoundAdvisor {
    param(
        [string]$Intent = "Ask local Phi-4 Mini to advise on the active Nexus wound.",
        [switch]$UsePhi,
        [switch]$RequirePhi
    )
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "Ask local Phi-4 Mini to advise on the active Nexus wound." }
    $args = @("-m", "nexus_gate.loops.phi_wound_advisor", "--root", ".", "--intent", $Intent, "--json")
    if ($UsePhi.IsPresent) { $args += "--call-model" }
    if ($RequirePhi.IsPresent) { $args += "--require-model" }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS Phi Wound Advisor failed." }
}

function Invoke-NexusToolbelt {
    param(
        [string]$View = "dashboard",
        [string]$Intent = "NEXUS AI Toolbelt cockpit.",
        [switch]$Json
    )
    if ([string]::IsNullOrWhiteSpace($View)) { $View = "dashboard" }
    if ([string]::IsNullOrWhiteSpace($Intent)) { $Intent = "NEXUS AI Toolbelt cockpit." }
    $args = @("-m", "nexus_gate.loops.toolbelt", "--root", ".", "--view", $View, "--intent", $Intent)
    if ($Json.IsPresent) { $args += "--json" }
    python @args
    if ($LASTEXITCODE -ne 0) { throw "NEXUS AI Toolbelt failed." }
}

switch ($Command) {
    "phi-gate-auto" { Invoke-NexusPhiGateSupervisor -Intent $Tag -GateName $Gate -Auto }
    "phi-gate" { Invoke-NexusPhiGateSupervisor -Intent $Tag -GateName $Gate }
    "phi-gate-compile" { Invoke-NexusPhiGateCompile }
    "meta-orchestrator" { Invoke-NexusMetaOrchestratorGate -Intent $Tag }
    "orchestrate" { Invoke-NexusLoopOrchestrator -Intent $Tag -Run:$Execute -Authorized:$HumanAuthorized }
    "phi-loop-auto" { Invoke-NexusPhiMicrodoseLoop -Intent $Tag -Auto }
    "phi-loop" { Invoke-NexusPhiMicrodoseLoop -Intent $Tag }
    "phi-wound-gpu" { Invoke-NexusPhiWoundAdvisor -Intent $Tag -UsePhi -RequirePhi }
    "phi-wound" { Invoke-NexusPhiWoundAdvisor -Intent $Tag -UsePhi:$CallModel }
    "preflight" { Invoke-NexusPreflightOptimizer -Intent $Tag }
    "preflight-json" { Invoke-NexusPreflightOptimizer -Intent $Tag -Json }
    "cortex" {
        $cortexIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($cortexIntent)) { $cortexIntent = "Run NEXUS Cortex gate." }
        python -m nexus_gate.cortex.compile --root . --intent $cortexIntent --json
        if ($LASTEXITCODE -ne 0) { throw "NEXUS Cortex gate failed." }
    }
    "cortex-refresh" {
        $cortexIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($cortexIntent)) { $cortexIntent = "Refresh Cortex certificate for NEXUS predictive memory orchestration." }
        python -m nexus_gate.cortex.refresh --root . --intent $cortexIntent --json
        if ($LASTEXITCODE -ne 0) { throw "NEXUS Cortex refresh failed." }
    }
    "sync-cortex" {
        $cortexSource = $Tag
        if ([string]::IsNullOrWhiteSpace($cortexSource)) { $cortexSource = "$env:USERPROFILE\OneDrive\Desktop\Cortex" }
        & (Join-Path $PSScriptRoot "sync_cortex.ps1") -Source $cortexSource -Root $Root
        if ($LASTEXITCODE -ne 0) { throw "NEXUS Cortex sync failed." }
    }
    "wound-compress" { Invoke-NexusWoundCompression -Intent $Tag }
    "toolbelt" { Invoke-NexusToolbelt -View "dashboard" -Intent $Tag }
    "toolbelt-json" { Invoke-NexusToolbelt -View "dashboard" -Intent $Tag -Json }
    "toolbelt-start" { Invoke-NexusToolbelt -View "start" -Intent $Tag }
    "toolbelt-dashboard" { Invoke-NexusToolbelt -View "dashboard" -Intent $Tag }
    "toolbelt-next" { Invoke-NexusToolbelt -View "next" -Intent $Tag }
    "toolbelt-ship" { Invoke-NexusToolbelt -View "ship" -Intent $Tag }


    "loop-registry" { Show-NexusLoopRegistry }
    "loops" { python -m nexus_gate.loops.runner --root . --list; if ($LASTEXITCODE -ne 0) { throw "NEXUS loop list failed." } }
    "meta-loop" { Invoke-NexusMetaLoop -LoopName $Loop -Intent $Tag -Run:$Execute -Authorized:$HumanAuthorized }
    "cell-policy" { Invoke-NexusCellPolicyCli }
    "cell-ledger" { Invoke-NexusCellLedgerCli }
    "cell-doctor" { Invoke-NexusCellDoctorCli }
    "cell" { Invoke-NexusCellDoctorCli }
    "cell-run" { Invoke-NexusCellRunCli }
    "cell-bridge" { Invoke-NexusCellBridge -Intent $Tag }
    "shell" { Invoke-NexusShell -Intent $Tag }
    "cell-context" { Invoke-NexusCellContext -Intent $Tag }
    "cell-plan" { Invoke-NexusCellPlan -Intent $Tag }
    "geo-clean" { Invoke-NexusGeoClean }
    "geo" { Invoke-NexusGeo -Intent $Tag }
    "fast" { Invoke-NexusNN -Intent $Tag -Role "FAST" -UseModel:$CallModel }
    "balanced" { Invoke-NexusNN -Intent $Tag -Role "BALANCED" -UseModel:$CallModel }
    "deep" { Invoke-NexusNN -Intent $Tag -Role "DEEP" -UseModel:$CallModel }
    "align-score" { python -m nexus_gate.nn_router.scorecard --root . --json; if ($LASTEXITCODE -ne 0) { throw "NEXUS drift scorecard failed." } }
    "nn" { Invoke-NexusNN -Intent $Tag -UseModel:$CallModel }
    "nn-health" { Invoke-NexusNN -Intent "NEXUS NN router health check: report local model roles and policy gates." }
    "tnn" { Invoke-NexusNN -Intent $Tag -Role "TNN" -UseModel:$CallModel }
    "tnn-chat" {
        python ".\Tesseract Neural Network\brain\stream_chat.py" --intent "$Tag"
        if ($LASTEXITCODE -ne 0) { throw "TNN streaming chat failed." }
    }
    "tnn-health" {
        python ".\Tesseract Neural Network\brain\bench_tnn_runtime.py"
        if ($LASTEXITCODE -ne 0) { throw "TNN runtime health failed." }
    }
    "tnn-doctor" {
        python ".\Tesseract Neural Network\brain\doctor_tnn_model.py"
        if ($LASTEXITCODE -ne 0) { Write-Warning "TNN model doctor returned non-zero." }
    }
    "tnn-warm" {
        python ".\Tesseract Neural Network\brain\prewarm_tnn_mistral.py"
        if ($LASTEXITCODE -ne 0) { Write-Warning "TNN warm returned non-zero; scaffold lane remains available." }
    }
    "tnn-deep" {
        python ".\Tesseract Neural Network\brain\stream_chat.py" --intent "$Tag" --model "tnn-mistral:latest" --deep
        if ($LASTEXITCODE -ne 0) { throw "TNN deep chat failed." }
    }
    "ask" { Invoke-NexusNN -Intent $Tag -UseModel:$CallModel }
    "rehydrate" {
        Show-Rehydration
        python -m nexus_gate.loops.predictive_timing --root . --json
        if ($LASTEXITCODE -ne 0) { throw "Predictive timing preflight failed." }
        Run-Compiler
        Write-Host "[OK] Rehydration complete."
    }
    "compile" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 compile }
    "strict" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_strict_compile.ps1 }
    "pack" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 pack }
    "adapters" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_adapter_compile.ps1 }
    "receptors" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_receptor_compile.ps1 }
    "bridge" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_bridge_demo.ps1 }
    "runtime" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 runtime }
    "human" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 all }
    "feedback" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 feedback }
    "interconnect" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 interconnect }
    "compact" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 compact }
    "heal" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 heal }
    "interface" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 interface }
    "electron-env" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 electron-env }
    "electron-preflight" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 electron-preflight }
    "reflect" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 reflect }
    "domain" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 domain }
    "predictive-timing" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 predictive-timing }
    "predictive-evolve" { python -m nexus_gate.loops.predictive_evolve --root . --json }
    "predictive-memory" {
        $memoryIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($memoryIntent)) { $memoryIntent = "Fuse Cortex memory and predictive gate evidence." }
        python -m nexus_gate.loops.predictive_memory_orchestrator --root . --intent $memoryIntent --json
    }
    "certificate-resume" { python -m nexus_gate.loops.certificate_resume --root . --json }
    "epoch-seal" { python -m nexus_gate.epochs.seal --root . --json }
    "epoch-observe" { python -m nexus_gate.epochs.seal --root . --json }
    "epoch-verify" { python -m nexus_gate.epochs.seal --root . --verify --json }
    "epoch-chain-verify" { python -m nexus_gate.epochs.seal --root . --chain-verify --json }
    "origin-seal" { python -m nexus_gate.origin.seal --root . --json }
    "triadic-lattice" { python -m nexus_gate.lattice.triadic --root . --json }
    "distill" { python -m nexus_gate.distillation.graph --root . --json }
    "decision-envelope" {
        $decisionIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($decisionIntent)) { $decisionIntent = "Self-bootstrap NEXUS decision envelope." }
        python -m nexus_gate.decision.envelope --root . --intent $decisionIntent --json
    }
    "coherence-field" {
        $coherenceIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($coherenceIntent)) { $coherenceIntent = "Compile NEXUS coherence continuity field." }
        python -m nexus_gate.coherence.field --root . --intent $coherenceIntent --json
    }
    "outcome-learn" {
        $outcomeIntent = $Tag
        if ([string]::IsNullOrWhiteSpace($outcomeIntent)) { $outcomeIntent = "Compile NEXUS recommendation outcome learning." }
        python -m nexus_gate.outcomes.learn --root . --intent $outcomeIntent --json
    }
    "runtime-hygiene" { python -m nexus_gate.hygiene.runtime_churn --root . --json }
    "clean-runtime" { python -m nexus_gate.hygiene.runtime_churn --root . --apply --json }
    "action-recommend" { python -m nexus_gate.actions.cli recommend --root . --json }
    "action-status" { python -m nexus_gate.actions.cli status --root . --action-id $ActionId --json }
    "action-authorize" { python -m nexus_gate.actions.cli authorize --root . --action-id $ActionId --note $Tag --json }
    "action-deny" { python -m nexus_gate.actions.cli deny --root . --action-id $ActionId --json }
    "action-execute" { python -m nexus_gate.actions.cli execute --root . --action-id $ActionId --json }
    "action-effects" { python -m nexus_gate.actions.cli effects --root . --action-id $ActionId --json }
    "action-final-evolve" { python -m nexus_gate.actions.cli action-final-evolve --root . --action-id $ActionId --json }
    "action-validate" { python -m nexus_gate.actions.cli validate --root . --action-id $ActionId --json }
    "action-finalize" { python -m nexus_gate.actions.cli finalize --root . --action-id $ActionId --json }
    "action-chain-verify" { python -m nexus_gate.actions.cli chain-verify --root . --json }
    "action-semantic-verify" {
        if ([string]::IsNullOrWhiteSpace($ActionId)) { python -m nexus_gate.actions.cli semantic-verify --root . --json }
        else { python -m nexus_gate.actions.cli semantic-verify --root . --action-id $ActionId --json }
    }
    "experience-readiness" { python -m nexus_gate.actions.cli experience-readiness --root . --json }
    "experience-seal" { python -m nexus_gate.actions.cli experience-seal --root . --action-id $ActionId --json }
    "experience-chain-verify" { python -m nexus_gate.actions.cli experience-chain-verify --root . --json }
    "calibration-status" { python -m nexus_gate.actions.cli calibration-status --root . --experience-id $ActionId --json }
    "calibration-authorize" { python -m nexus_gate.actions.cli calibration-authorize --root . --experience-id $ActionId --note $Tag --json }
    "calibration-apply" { python -m nexus_gate.actions.cli calibration-apply --root . --experience-id $ActionId --json }
    "calibration-replay-verify" { python -m nexus_gate.actions.cli calibration-replay-verify --root . --json }
    "adaptive-coherence" { python -m nexus_gate.actions.cli adaptive-coherence --root . --json }
    "emergence-report" { python -m nexus_gate.actions.cli emergence-report --root . --json }
    "causal-receipts" { python -m nexus_gate.actions.cli receipts --root . --json }
    "first-learning-readiness" { python -m nexus_gate.actions.cli first-learning-readiness --root . --json }
    "install-hooks" { & (Join-Path $PSScriptRoot "install_nexus_git_hooks.ps1") -Root $Root }
    "algorithm-cards" { python -m nexus_gate.algorithms.cards --root . --json }
    "discovery-cards" { python -m nexus_gate.discoveries.cards --root . --json }
    "tui" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_tui.ps1 }
    "ui" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_ui.ps1 }
    "evolve" { powershell -ExecutionPolicy Bypass -File .\scripts\nexus_human.ps1 evolve }
    "once" { Run-Compiler; Write-Host "[OK] Once passed." }
    "loop" { Run-Loop -MaxCycles $Cycles -SleepSeconds $Interval }
    "watch" { Run-Loop -MaxCycles 1 -SleepSeconds $Interval -Forever }
    "status" { Show-Status }
    "promote" { Promote }
}
