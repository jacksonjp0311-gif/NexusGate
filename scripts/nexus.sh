#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cmd="${1:-rehydrate}"
shift || true

cycles=1
interval=5
tag=""
no_commit=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cycles) cycles="$2"; shift 2 ;;
    --interval) interval="$2"; shift 2 ;;
    --tag) tag="$2"; shift 2 ;;
    --no-commit) no_commit=1; shift ;;
    *) echo "[FAIL] Unknown argument: $1"; exit 2 ;;
  esac
done

py() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    python "$@"
  fi
}

run_compiler() { py -m nexus_gate.compiler --root . --json; }

show_rehydration() {
  echo "[NG] Rehydration visibility"
  [[ -f docs/goal/GOAL_LOCK.md ]] && sed -n '1,80p' docs/goal/GOAL_LOCK.md
  [[ -f docs/adapters/ADAPTER_REGISTRY.md ]] && sed -n '1,80p' docs/adapters/ADAPTER_REGISTRY.md
  [[ -f docs/receptors/RECEPTOR_REGISTRY.md ]] && sed -n '1,80p' docs/receptors/RECEPTOR_REGISTRY.md
  [[ -f docs/bridge/BRIDGE_SESSION_RUNNER.md ]] && sed -n '1,80p' docs/bridge/BRIDGE_SESSION_RUNNER.md
  [[ -f docs/bridge/BOUNDED_BRIDGE_RUNTIME.md ]] && sed -n '1,80p' docs/bridge/BOUNDED_BRIDGE_RUNTIME.md
  [[ -f docs/failure_modes/FAILURE_MODE_CHART.md ]] && sed -n '1,80p' docs/failure_modes/FAILURE_MODE_CHART.md
  [[ -f docs/updates/UPDATE_CHART.md ]] && sed -n '1,80p' docs/updates/UPDATE_CHART.md
  [[ -f reports/nexus_compile_report_latest.json ]] && cat reports/nexus_compile_report_latest.json
}

show_status() {
  echo "[NG] NEXUS GATE STATUS"
  [[ -f state/goal_lock.v0.1.6.json ]] && cat state/goal_lock.v0.1.6.json
  [[ -f state/adapter_registry_index.v0.1.7.json ]] && cat state/adapter_registry_index.v0.1.7.json
  [[ -f state/receptor_registry_index.v0.1.8.json ]] && cat state/receptor_registry_index.v0.1.8.json
  [[ -f state/bridge_session_index.v0.1.9.json ]] && cat state/bridge_session_index.v0.1.9.json
  [[ -f state/bounded_bridge_runtime_index.v0.2.0.json ]] && cat state/bounded_bridge_runtime_index.v0.2.0.json
  [[ -f reports/nexus_runtime_compile_report_latest.json ]] && cat reports/nexus_runtime_compile_report_latest.json
  [[ -f reports/nexus_bounded_runtime_report_latest.json ]] && cat reports/nexus_bounded_runtime_report_latest.json
  [[ -f reports/nexus_bridge_compile_report_latest.json ]] && cat reports/nexus_bridge_compile_report_latest.json
  [[ -f reports/nexus_compile_report_latest.json ]] && cat reports/nexus_compile_report_latest.json
  [[ -f dist/nexus_gate_pack_manifest_latest.json ]] && cat dist/nexus_gate_pack_manifest_latest.json
  git status --short || true
}

run_loop() {
  local forever="$1"
  local i=0
  while true; do
    i=$((i + 1))
    echo "[NG] Cycle $i"
    run_compiler
    if [[ "$forever" != "1" && "$i" -ge "$cycles" ]]; then break; fi
    sleep "$interval"
  done
}

promote() {
  run_compiler
  py -m nexus_gate.adapters.compile --root .
  py -m nexus_gate.receptors.compile --root .
  py -m nexus_gate.bridge.compile --root .
  py -m nexus_gate.bridge.runtime_compiler --root .
  py -m nexus_gate.build.packer --root . --out dist
  if command -v git >/dev/null 2>&1 && [[ "$no_commit" -ne 1 ]]; then
    git add .
    if [[ -n "$(git status --porcelain)" ]]; then
      git commit -m "chore: promote NEXUS GATE bounded runtime packed pass"
    fi
  fi
  if command -v git >/dev/null 2>&1 && [[ -n "$tag" ]]; then git tag "$tag"; fi
  echo "[OK] Promotion gate passed."
}

case "$cmd" in
  rehydrate) show_rehydration; run_compiler; echo "[OK] Rehydration complete." ;;
  compile) run_compiler; echo "[OK] Compile passed." ;;
  strict) bash scripts/nexus_strict_compile.sh ;;
  pack) bash scripts/nexus_pack.sh ;;
  adapters) bash scripts/nexus_adapter_compile.sh ;;
  receptors) bash scripts/nexus_receptor_compile.sh ;;
  bridge) bash scripts/nexus_bridge_demo.sh ;;
  runtime) bash scripts/nexus_runtime.sh ;;
  once) run_compiler; echo "[OK] Once passed." ;;
  loop) run_loop 0 ;;
  watch) run_loop 1 ;;
  status) show_status ;;
  promote) promote ;;
  *) echo "[FAIL] Unknown command: $cmd"; echo "Commands: rehydrate, compile, strict, pack, adapters, receptors, bridge, runtime, once, loop, watch, status, promote"; exit 2 ;;
esac
