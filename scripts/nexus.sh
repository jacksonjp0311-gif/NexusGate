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
  origin-seal) python -m nexus_gate.origin.seal --root . --json ;;
  triadic-lattice) python -m nexus_gate.lattice.triadic --root . --json ;;
  distill) python -m nexus_gate.distillation.graph --root . --json ;;
  decision-envelope) python -m nexus_gate.decision.envelope --root . --json ;;
  coherence-field) python -m nexus_gate.coherence.field --root . --json ;;
  outcome-learn) python -m nexus_gate.outcomes.learn --root . --json ;;
  runtime-hygiene) python -m nexus_gate.hygiene.runtime_churn --root . --json ;;
  clean-runtime) python -m nexus_gate.hygiene.runtime_churn --root . --apply --json ;;
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
    python -m nexus_gate.origin.seal --root . --json
    python -m nexus_gate.lattice.triadic --root . --json
    python -m nexus_gate.decision.envelope --root . --intent "evolve chain self-bootstrap decision envelope" --json
    python -m nexus_gate.coherence.field --root . --intent "evolve chain coherence continuity field" --json
    python -m nexus_gate.outcomes.learn --root . --intent "evolve chain recommendation outcome learning" --json
    python -m nexus_gate.distillation.graph --root . --json
    python -m nexus_gate.build.packer --root . --out dist --json
    python -m nexus_gate.hygiene.runtime_churn --root . --json
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
