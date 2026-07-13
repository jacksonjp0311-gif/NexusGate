#!/usr/bin/env bash
set -euo pipefail
# NEXUS GATE compact Bash command surface
# Rehydration/compatibility markers retained for audit/tests:
# FAILURE_MODE_CHART
# UPDATE_CHART
# strict
# tui
# ui
# reflect
# domain
# geo
# geo-clean
# phi-wound
# phi-wound-gpu
# toolbelt
# toolbelt-dashboard
# toolbelt-next
# preflight
# preflight-json
# meta-orchestrator
# orchestrate
# toolbelt-ship
# toolbelt|toolbelt-dashboard compatibility marker for v0.9.6 tests
# wound-compress
# cortex
  # origin-seal
  # epoch-seal
  # triadic-lattice
  # distill
  # decision-envelope
  # coherence-field
  # outcome-learn
  # runtime-hygiene
# predictive-memory
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMMAND="${1:-rehydrate}"

run_meta_loop() {
  local loop_name="${1:-rhp-core}"
  shift || true
  local intent="${*:-Nexus meta loop trigger.}"
  python -m nexus_gate.loops.runner --root . --loop "$loop_name" --intent "$intent"
}

run_meta_loop_exec() {
  local loop_name="${1:-rhp-core}"
  shift || true
  local intent="${*:-Nexus meta loop trigger.}"
  python -m nexus_gate.loops.runner --root . --loop "$loop_name" --intent "$intent" --execute --human-authorized --json
}

case "$COMMAND" in

  phi-gate)
    export NEXUS_PHI4_MINI_COMMAND='python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    python -m nexus_gate.loops.phi_gate_supervisor --root . --intent "${TAG:-Run Phi Gate Supervisor.}" --gate "${GATE:-ci-core}" --call-model
    ;;
  phi-gate-auto)
    export NEXUS_PHI4_MINI_COMMAND='python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    python -m nexus_gate.loops.phi_gate_supervisor --root . --intent "${TAG:-Run Phi Gate Supervisor.}" --gate "${GATE:-ci-core}" --call-model --auto-repair --human-authorized
    ;;
  phi-gate-compile)
    python -m nexus_gate.loops.phi_gate_supervisor_compile --root . --json
    ;;
  meta-orchestrator)
    shift || true
    INTENT="${*:-Compile the NEXUS meta-orchestrator gate.}"
    python -m nexus_gate.loops.meta_orchestrator_gate --root . --intent "$INTENT" --json
    ;;
  orchestrate)
    shift || true
    INTENT="${*:-Orchestrate the next NEXUS loop.}"
    python -m nexus_gate.loops.orchestrator --root . --intent "$INTENT" --json
    ;;

  phi-wound)
    shift || true
    CALL_MODEL=""
    if [ "${1:-}" = "--call-model" ]; then CALL_MODEL="--call-model"; shift || true; fi
    INTENT="${*:-Ask local Phi-4 Mini to advise on the active Nexus wound.}"
    python -m nexus_gate.loops.phi_wound_advisor --root . --intent "$INTENT" $CALL_MODEL --json
    ;;
  phi-wound-gpu)
    shift || true
    INTENT="${*:-Ask local GPU Phi-4 Mini to advise on the active Nexus wound.}"
    python -m nexus_gate.loops.phi_wound_advisor --root . --intent "$INTENT" --call-model --require-model --json
    ;;

  preflight)
    shift || true
    INTENT="${*:-Preflight next Nexus mutation surface.}"
    python -m nexus_gate.loops.preflight_optimizer --root . --intent "$INTENT"
    ;;
  preflight-json)
    shift || true
    INTENT="${*:-Preflight next Nexus mutation surface.}"
    python -m nexus_gate.loops.preflight_optimizer --root . --intent "$INTENT" --json
    ;;
  wound-compress)
    shift || true
    INTENT="${*:-Compress active Nexus wound.}"
    python -m nexus_gate.loops.wound_compression --root . --intent "$INTENT" --json
    ;;
  # NEXUS_TOOLBELT_CONSOLE_V096_BASH_PARITY
  # Compatibility marker for legacy tests/docs: toolbelt|toolbelt-dashboard
  toolbelt)
    shift || true
    INTENT="${*:-Nexus Toolbelt cockpit.}"
    python -m nexus_gate.loops.toolbelt --root . --intent "$INTENT" --json
    ;;

  toolbelt-json)
    shift || true
    INTENT="${*:-Nexus Toolbelt JSON packet.}"
    python -m nexus_gate.loops.toolbelt --root . --view dashboard --intent "$INTENT" --json
    ;;
  toolbelt-start)
    shift || true
    INTENT="${*:-Nexus Toolbelt start.}"
    python -m nexus_gate.loops.runner --root . --loop toolbelt-start --intent "$INTENT" --execute --human-authorized --json
    ;;
  toolbelt-dashboard)
    shift || true
    INTENT="${*:-Nexus Toolbelt dashboard.}"
    python -m nexus_gate.loops.runner --root . --loop toolbelt-dashboard --intent "$INTENT" --execute --human-authorized --json
    ;;
  toolbelt-next)
    shift || true
    INTENT="${*:-Nexus Toolbelt next action.}"
    python -m nexus_gate.loops.runner --root . --loop toolbelt-next --intent "$INTENT" --execute --human-authorized --json
    ;;
  toolbelt-ship)
    shift || true
    INTENT="${*:-Nexus Toolbelt ship check.}"
    python -m nexus_gate.loops.runner --root . --loop toolbelt-ship --intent "$INTENT" --execute --human-authorized --json
    ;;
  toolbelt|toolbelt-dashboard)
    shift || true
    INTENT="${*:-NEXUS AI Toolbelt Console.}"
    python -m nexus_gate.loops.toolbelt --root . --intent "$INTENT" --json
    ;;
  toolbelt-start)
    shift || true
    run_meta_loop_exec toolbelt-start "${*:-Start from the AI Toolbelt.}"
    ;;
  toolbelt-next)
    shift || true
    run_meta_loop_exec toolbelt-next "${*:-Recommend the next local loop from toolbelt evidence.}"
    ;;
  toolbelt-ship)
    shift || true
    run_meta_loop_exec toolbelt-ship-console "${*:-Prepare the Toolbelt ship console.}"
    ;;
  toolbelt-process)
    shift || true
    run_meta_loop_exec toolbelt-process "${*:-Run the governed Toolbelt process.}"
    ;;
  loops)
    python -m nexus_gate.loops.runner --root . --list
    ;;
  loop-registry)
    cat loops/nexus_loop_registry.v0.1.json
    ;;
  meta-loop)
    shift || true
    run_meta_loop "${1:-rhp-core}" "${@:2}"
    ;;
  geo-clean)
    python -m nexus_gate.geometric_memory.cleanup --root . --json
    ;;
  geo)
    shift || true
    INTENT="${*:-What should we do next?}"
    python -m nexus_gate.geometric_memory.router --root . --intent "$INTENT" --json
    ;;
  compile|strict)
    python -m nexus_gate.compiler --root . --json
    ;;
  adapters) python -m nexus_gate.adapters.compile --root . --json ;;
  receptors) python -m nexus_gate.receptors.compile --root . --json ;;
  bridge) python -m nexus_gate.bridge.compile --root . --json ;;
  runtime) python -m nexus_gate.bridge.runtime_compiler --root . --json ;;
  compact) python -m nexus_gate.evidence.compact --root . --json ;;
  interconnect) python -m nexus_gate.interconnect.compile --root . --json ;;
  feedback) python -m nexus_gate.feedback.compile --root . --json ;;
  heal) python -m nexus_gate.self_healing.compile --root . --json ;;
  interface) python -m nexus_gate.feedback.interface_compile --root . --json ;;
  electron-env) python -m nexus_gate.ui.electron_environment_compile --root . --json ;;
  electron-preflight) python -m nexus_gate.ui.electron_preflight_compile --root . --json ;;
  reflect) python -m nexus_gate.reflection.compile --root . --json ;;
  domain) python -m nexus_gate.domain.compile --root . --json ;;
  predictive-timing) python -m nexus_gate.loops.predictive_timing --root . --json ;;
  predictive-evolve) python -m nexus_gate.loops.predictive_evolve --root . --json ;;
  predictive-memory)
    shift || true
    INTENT="${*:-Fuse Cortex memory and predictive gate evidence.}"
    python -m nexus_gate.loops.predictive_memory_orchestrator --root . --intent "$INTENT" --json
    ;;
  certificate-resume) python -m nexus_gate.loops.certificate_resume --root . --json ;;
  epoch-seal) python -m nexus_gate.epochs.seal --root . --json ;;
  epoch-observe) python -m nexus_gate.epochs.seal --root . --json ;;
  epoch-verify) python -m nexus_gate.epochs.seal --root . --verify --json ;;
  epoch-chain-verify) python -m nexus_gate.epochs.seal --root . --chain-verify --json ;;
  origin-seal) python -m nexus_gate.origin.seal --root . --json ;;
  triadic-lattice) python -m nexus_gate.lattice.triadic --root . --json ;;
  distill) python -m nexus_gate.distillation.graph --root . --json ;;
  decision-envelope) python -m nexus_gate.decision.envelope --root . --json ;;
  coherence-field) python -m nexus_gate.coherence.field --root . --json ;;
  outcome-learn) python -m nexus_gate.outcomes.learn --root . --json ;;
  runtime-hygiene) python -m nexus_gate.hygiene.runtime_churn --root . --json ;;
  clean-runtime) python -m nexus_gate.hygiene.runtime_churn --root . --apply --json ;;
  breath) python -m nexus_gate.breath.pulse --root . --json ;;
  telemetry-sources) python -m nexus_gate.telemetry.cli sources --root . --json ;;
  telemetry-health) python -m nexus_gate.telemetry.cli health --root . --json ;;
  telemetry-pull) python -m nexus_gate.telemetry.cli pull --root . --profile "${TAG:-space-weather}" --json ;;
  telemetry-fuse) python -m nexus_gate.telemetry.cli fuse --root . --json ;;
  telemetry-status) python -m nexus_gate.telemetry.cli status --root . --json ;;
  conductance-field) python -m nexus_gate.field.cli field --root . --intent "${TAG:-Compile NEXUS conductance field.}" --json ;;
  conductance-status) python -m nexus_gate.field.cli status --root . --intent "${TAG:-Inspect NEXUS conductance field.}" --json ;;
  conductance-route) python -m nexus_gate.field.cli route --root . --intent "${TAG:-Route through NEXUS conductance field.}" --json ;;
  conductance-replay-verify) python -m nexus_gate.field.cli replay-verify --root . --json ;;
  conductance-calibration-proposal) python -m nexus_gate.field.cli calibration-proposal --root . --intent "$TAG" --json ;;
  ai-touch-begin)
    shift || true
    python -m nexus_gate.intelligence.cli touch-begin --root . --provider "${PROVIDER:-codex}" --session-id "${SESSION_ID:-manual}" --intent "${*:-${TAG:-Declared AI touch session.}}" --json
    ;;
  ai-touch-status) python -m nexus_gate.intelligence.cli touch-status --root . --interaction-id "${INTERACTION_ID:-}" --json ;;
  ai-touch-list) python -m nexus_gate.intelligence.cli touch-list --root . --json ;;
  ai-touch-end)
    shift || true
    python -m nexus_gate.intelligence.cli touch-end --root . --interaction-id "${1:-${INTERACTION_ID:-}}" --disposition "${DISPOSITION:-pending_review}" --json
    ;;
  ai-touch-abort)
    shift || true
    python -m nexus_gate.intelligence.cli touch-abort --root . --interaction-id "${1:-${INTERACTION_ID:-}}" --json
    ;;
  ai-touch-verify) python -m nexus_gate.intelligence.cli touch-verify --root . --interaction-id "${INTERACTION_ID:-}" --json ;;
  ai-touch-replay-verify) python -m nexus_gate.intelligence.cli touch-replay-verify --root . --json ;;
  intelligence-extract)
    shift || true
    python -m nexus_gate.intelligence.cli extract --root . --interaction-id "${1:-${INTERACTION_ID:-}}" --json
    ;;
  intelligence-status) python -m nexus_gate.intelligence.cli intelligence-status --root . --json ;;
  intelligence-candidates|intelligence-review) python -m nexus_gate.intelligence.cli intelligence-candidates --root . --json ;;
  intelligence-promote)
    shift || true
    python -m nexus_gate.intelligence.cli promote --root . --candidate-id "${1:-${CANDIDATE_ID:-}}" --json
    ;;
  intelligence-reject)
    shift || true
    python -m nexus_gate.intelligence.cli reject --root . --candidate-id "${1:-${CANDIDATE_ID:-}}" --json
    ;;
  intelligence-replay-verify) python -m nexus_gate.intelligence.cli intelligence-replay-verify --root . --json ;;
  language-corpus-build) python -m nexus_gate.language.cli corpus-build --root . --json ;;
  language-corpus-status) python -m nexus_gate.language.cli corpus-status --root . --json ;;
  language-corpus-verify) python -m nexus_gate.language.cli corpus-verify --root . --json ;;
  language-query)
    shift || true
    python -m nexus_gate.language.cli query --root . --tag "${*:-${TAG:-What is NEXUS permitted to learn?}}" --json
    ;;
  language-explain)
    shift || true
    python -m nexus_gate.language.cli explain --root . --tag "${*:-${TAG:-Explain NEXUS.}}" --json
    ;;
  language-chat)
    shift || true
    python -m nexus_gate.language.cli chat --root . --tag "${*:-${TAG:-What is pending?}}" --json
    ;;
  language-trace)
    shift || true
    python -m nexus_gate.language.cli trace --root . --tag "${*:-${TAG:-Trace NEXUS language activation.}}" --json
    ;;
  language-status) python -m nexus_gate.language.cli status --root . --json ;;
  self-model-build) python -m nexus_gate.language.cli self-model-build --root . --json ;;
  self-model-status) python -m nexus_gate.language.cli self-model-status --root . --json ;;
  self-model-verify) python -m nexus_gate.language.cli self-model-verify --root . --json ;;
  language-benchmark) python -m nexus_gate.language.cli benchmark --root . --json ;;
  language-benchmark-smoke) python -m nexus_gate.language.cli benchmark-smoke --root . --json ;;
  language-benchmark-full) python -m nexus_gate.language.cli benchmark-full --root . --json ;;
  language-benchmark-compare) python -m nexus_gate.language.cli benchmark-compare --root . --json ;;
  language-retention-test) python -m nexus_gate.language.cli retention-test --root . --json ;;
  language-efficiency-report) python -m nexus_gate.language.cli efficiency-report --root . --json ;;
  language-adversarial-test) python -m nexus_gate.language.cli adversarial-test --root . --json ;;
  language-replay-verify) python -m nexus_gate.language.cli replay-verify --root . --json ;;
  motif-discover) python -m nexus_gate.language.cli motif-discover --root . --json ;;
  motif-status) python -m nexus_gate.language.cli motif-status --root . --json ;;
  motif-verify) python -m nexus_gate.language.cli motif-verify --root . --json ;;
  motif-expand) python -m nexus_gate.language.cli motif-status --root . --json ;;
  motif-replay-verify) python -m nexus_gate.language.cli motif-replay-verify --root . --json ;;
  language-calibration-status) python -m nexus_gate.language.cli calibration-status --root . --json ;;
  language-calibration-propose) python -m nexus_gate.language.cli calibration-propose --root . --json ;;
  language-calibration-authorize) python -m nexus_gate.language.cli calibration-authorize --root . --json ;;
  language-calibration-apply) python -m nexus_gate.language.cli calibration-apply --root . --json ;;
  language-calibration-replay-verify) python -m nexus_gate.language.cli calibration-replay-verify --root . --json ;;
  nex-teach-begin)
    shift || true
    python -m nexus_gate.nex_core.cli teach-begin --root . --tag "${*:-${TAG:-NEX teaching episode.}}" --json
    ;;
  nex-teach-status|nex-teach-list) python -m nexus_gate.nex_core.cli teach-status --root . --json ;;
  nex-teach-bind-validation)
    shift || true
    TEACHING_ID="${1:-${ACTION_ID:-}}"
    shift || true
    python -m nexus_gate.nex_core.cli teach-bind-validation --root . --teaching-id "$TEACHING_ID" --tag "${*:-${TAG:-}}" --json
    ;;
  nex-teach-seal)
    shift || true
    python -m nexus_gate.nex_core.cli teach-seal --root . --teaching-id "${1:-${ACTION_ID:-}}" --disposition "${DISPOSITION:-pending_review}" --json
    ;;
  nex-teach-abort)
    shift || true
    python -m nexus_gate.nex_core.cli teach-abort --root . --teaching-id "${1:-${ACTION_ID:-}}" --json
    ;;
  nex-teach-verify)
    shift || true
    python -m nexus_gate.nex_core.cli teach-verify --root . --teaching-id "${1:-${ACTION_ID:-}}" --json
    ;;
  nex-teach-replay-verify) python -m nexus_gate.nex_core.cli teach-replay-verify --root . --json ;;
  nex-chat|nex-query|nex-explain)
    sub="${COMMAND#nex-}"
    shift || true
    python -m nexus_gate.nex_core.cli "$sub" --root . --prompt "${*:-${TAG:-What has NEX verified about its own learning?}}" --json
    ;;
  nex-inner-status) python -m nexus_gate.nex_core.cli inner-status --root . --json ;;
  nex-inner-trace) python -m nexus_gate.nex_core.cli inner-trace --root . --json ;;
  nex-cycle-status) python -m nexus_gate.nex_core.cli cycle-status --root . --json ;;
  nex-mode-status) python -m nexus_gate.nex_core.cli mode-status --root . --json ;;
  nex-learn-status) python -m nexus_gate.nex_core.cli learn-status --root . --json ;;
  nex-learn-propose) python -m nexus_gate.nex_core.cli learn-propose --root . --json ;;
  nex-learn-inspect|nex-learn-authorize|nex-learn-apply|nex-learn-reject|nex-learn-rollback-propose)
    sub="${COMMAND#nex-}"
    shift || true
    python -m nexus_gate.nex_core.cli "$sub" --root . --proposal-id "${1:-${ACTION_ID:-}}" --json
    ;;
  nex-learn-replay-verify) python -m nexus_gate.nex_core.cli learn-replay-verify --root . --json ;;
  nex-verify|nex-verify-cycle|nex-verify-learning|nex-verify-authority|nex-verify-retention|nex-verify-benchmark|nex-verify-adversarial|nex-verify-replay|nex-verify-all)
    sub="${COMMAND#nex-}"
    shift || true
    python -m nexus_gate.nex_core.cli "$sub" --root . --proposal-id "${1:-${ACTION_ID:-}}" --json
    ;;
  action-recommend) python -m nexus_gate.actions.cli recommend --root . --json ;;
  action-status)
    shift || true
    python -m nexus_gate.actions.cli status --root . --action-id "${1:-}" --json
    ;;
  action-authorize)
    shift || true
    ACTION_ID="${1:-}"
    shift || true
    python -m nexus_gate.actions.cli authorize --root . --action-id "$ACTION_ID" --note "${*:-}" --json
    ;;
  action-deny)
    shift || true
    python -m nexus_gate.actions.cli deny --root . --action-id "${1:-}" --json
    ;;
  action-execute)
    shift || true
    python -m nexus_gate.actions.cli execute --root . --action-id "${1:-}" --json
    ;;
  action-effects)
    shift || true
    python -m nexus_gate.actions.cli effects --root . --action-id "${1:-}" --json
    ;;
  action-final-evolve)
    shift || true
    python -m nexus_gate.actions.cli action-final-evolve --root . --action-id "${1:-}" --json
    ;;
  action-validate)
    shift || true
    python -m nexus_gate.actions.cli validate --root . --action-id "${1:-}" --json
    ;;
  action-finalize)
    shift || true
    python -m nexus_gate.actions.cli finalize --root . --action-id "${1:-}" --json
    ;;
  action-chain-verify) python -m nexus_gate.actions.cli chain-verify --root . --json ;;
  action-semantic-verify)
    shift || true
    python -m nexus_gate.actions.cli semantic-verify --root . --action-id "${1:-}" --json
    ;;
  experience-readiness) python -m nexus_gate.actions.cli experience-readiness --root . --json ;;
  experience-chain-verify) python -m nexus_gate.actions.cli experience-chain-verify --root . --json ;;
  calibration-replay-verify) python -m nexus_gate.actions.cli calibration-replay-verify --root . --json ;;
  adaptive-coherence) python -m nexus_gate.actions.cli adaptive-coherence --root . --json ;;
  emergence-report) python -m nexus_gate.actions.cli emergence-report --root . --json ;;
  experience-seal)
    shift || true
    python -m nexus_gate.actions.cli experience-seal --root . --action-id "${1:-}" --json
    ;;
  calibration-status)
    shift || true
    python -m nexus_gate.actions.cli calibration-status --root . --experience-id "${1:-}" --json
    ;;
  calibration-authorize)
    shift || true
    EXP_ID="${1:-}"
    shift || true
    python -m nexus_gate.actions.cli calibration-authorize --root . --experience-id "$EXP_ID" --note "${*:-}" --json
    ;;
  calibration-apply)
    shift || true
    python -m nexus_gate.actions.cli calibration-apply --root . --experience-id "${1:-}" --json
    ;;
  causal-receipts) python -m nexus_gate.actions.cli receipts --root . --json ;;
  first-learning-readiness) python -m nexus_gate.actions.cli first-learning-readiness --root . --json ;;
  install-hooks) ./scripts/install_nexus_git_hooks.sh ;;
  cortex)
    shift || true
    INTENT="${*:-Run NEXUS Cortex gate.}"
    python -m nexus_gate.cortex.compile --root . --intent "$INTENT" --json
    ;;
  cortex-refresh)
    shift || true
    INTENT="${*:-Refresh Cortex certificate for NEXUS predictive memory orchestration.}"
    python -m nexus_gate.cortex.refresh --root . --intent "$INTENT" --json
    ;;
  sync-cortex)
    shift || true
    SOURCE="${1:-${HOME}/OneDrive/Desktop/Cortex}"
    ./scripts/sync_cortex.sh "$SOURCE"
    ;;
  algorithm-cards) python -m nexus_gate.algorithms.cards --root . --json ;;
  discovery-cards) python -m nexus_gate.discoveries.cards --root . --json ;;
  tui) echo "PowerShell TUI is Windows-only. Run: .\\scripts\\nexus.ps1 tui" ;;
  ui) echo "Compatibility UI alias is Windows-only. Run: .\\scripts\\nexus.ps1 ui" ;;
  cell|cell-doctor) python -m nexus_gate.nexus_cell.cli doctor --root . ;;
  cell-run) python -m nexus_gate.nexus_cell.cli run --root . --runner mock --payload ./NexusCell/examples/hello.ps1 ;;
  cell-ledger) python -m nexus_gate.nexus_cell.cli ledger --root . ;;
  cell-policy) python -m nexus_gate.nexus_cell.cli policy --root . ;;
  evolve)
    python -m compileall nexus_gate tests
    python -m unittest discover -s tests
    python -m nexus_gate.compiler --root . --json
    python -m nexus_gate.adapters.compile --root . --json
    python -m nexus_gate.receptors.compile --root . --json
    python -m nexus_gate.bridge.compile --root . --json
    python -m nexus_gate.bridge.runtime_compiler --root . --json
    python -m nexus_gate.evidence.compact --root . --json
    python -m nexus_gate.interconnect.compile --root . --json
    python -m nexus_gate.feedback.compile --root . --json
    python -m nexus_gate.self_healing.compile --root . --json
    python -m nexus_gate.feedback.interface_compile --root . --json
    python -m nexus_gate.ui.electron_environment_compile --root . --json
    python -m nexus_gate.ui.electron_preflight_compile --root . --json
    python -m nexus_gate.reflection.compile --root . --json
    python -m nexus_gate.domain.compile --root . --json
    python -m nexus_gate.loops.meta_orchestrator_gate --root . --intent "evolve chain meta-orchestrator seal" --json
    python -m nexus_gate.loops.orchestrator --root . --intent "evolve chain loop orchestration plan" --json
    python -m nexus_gate.loops.predictive_timing --root . --json
    python -m nexus_gate.loops.predictive_memory_orchestrator --root . --intent "evolve chain Cortex memory and predictive gate fusion" --json
    python -m nexus_gate.epochs.seal --root . --json
    python -m nexus_gate.origin.seal --root . --json
    python -m nexus_gate.lattice.triadic --root . --json
    python -m nexus_gate.decision.envelope --root . --intent "evolve chain self-bootstrap decision envelope" --json
    python -m nexus_gate.coherence.field --root . --intent "evolve chain coherence continuity field" --json
    python -m nexus_gate.outcomes.learn --root . --intent "evolve chain recommendation outcome learning" --json
    python -m nexus_gate.distillation.graph --root . --json
    python -m nexus_gate.build.packer --root . --out dist --json
    python -m nexus_gate.hygiene.runtime_churn --root . --json
    python -m nexus_gate.telemetry.cli health --root . --json
    python -m nexus_gate.telemetry.cli fuse --root . --json
    python -m nexus_gate.breath.pulse --root . --json
    python -m nexus_gate.field.cli field --root . --json
    python -m nexus_gate.field.cli replay-verify --root . --json
    ;;
  pack)
    python -m nexus_gate.build.packer --root . --out dist --json
    ;;
  status)
    test -f reports/nexus_toolbelt_console_latest.json && cat reports/nexus_toolbelt_console_latest.json || true
    test -f reports/nexus_feedback_interface_report_latest.json && cat reports/nexus_feedback_interface_report_latest.json || true
    ;;
  rehydrate)
    python -m nexus_gate.loops.predictive_timing --root . --json
    python -m nexus_gate.compiler --root . --json
    ;;
  phi-loop)
    export NEXUS_PHI4_MINI_COMMAND='python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    python -m nexus_gate.loops.phi_microdose_loop --root . --intent "${2:-Run bounded Phi microdose loop.}" --call-model
    ;;
  phi-loop-auto)
    export NEXUS_PHI4_MINI_COMMAND='python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    python -m nexus_gate.loops.phi_microdose_loop --root . --intent "${2:-Run bounded Phi microdose loop.}" --call-model --run-gates
    ;;
*)
    python -m nexus_gate.compiler --root . --json
    ;;
esac
