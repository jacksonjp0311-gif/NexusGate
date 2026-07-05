#!/usr/bin/env bash
set -euo pipefail
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
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMMAND="${1:-rehydrate}"

case "$COMMAND" in
  geo-clean)
    python -m nexus_gate.geometric_memory.cleanup --root . --json
    ;;
  geo)
    shift || true
    INTENT="${1:-What should we do next?}"
    python -m nexus_gate.geometric_memory.router --root . --intent "$INTENT" --json
    ;;
  compile) python -m nexus_gate.compiler --root . --json ;;
  strict) python -m nexus_gate.compiler --root . --json ;;
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
  tui) echo "PowerShell TUI is Windows-only. Run: .\\scripts\\nexus.ps1 tui" ;;
  ui) echo "Compatibility UI alias is Windows-only. Run: .\\scripts\\nexus.ps1 ui" ;;
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
    python -m nexus_gate.build.packer --root . --out dist --json
    ;;
  pack) python -m nexus_gate.build.packer --root . --out dist --json ;;
  status)
    test -f reports/nexus_feedback_interface_report_latest.json && cat reports/nexus_feedback_interface_report_latest.json
    ;;
  rehydrate|*)
    python -m nexus_gate.compiler --root . --json
    ;;
esac

