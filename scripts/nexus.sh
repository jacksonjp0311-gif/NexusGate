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
    --cycles)
      cycles="$2"
      shift 2
      ;;
    --interval)
      interval="$2"
      shift 2
      ;;
    --tag)
      tag="$2"
      shift 2
      ;;
    --no-commit)
      no_commit=1
      shift
      ;;
    *)
      echo "[FAIL] Unknown argument: $1"
      exit 2
      ;;
  esac
done

py() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    python "$@"
  fi
}

run_compiler() {
  py -m nexus_gate.compiler --root . --json
}

show_rehydration() {
  echo "[NG] Rehydration visibility"
  echo "[NG] Failure chart"
  sed -n '1,80p' docs/failure_modes/FAILURE_MODE_CHART.md
  echo
  echo "[NG] Update chart"
  sed -n '1,80p' docs/updates/UPDATE_CHART.md
  echo
  if [[ -f docs/evidence/COLD_EVIDENCE_ENGINE.md ]]; then
    echo "[NG] Cold evidence"
    sed -n '1,80p' docs/evidence/COLD_EVIDENCE_ENGINE.md
  fi
  echo
  if [[ -f reports/nexus_compile_report_latest.json ]]; then
    echo "[NG] Latest compiler report"
    cat reports/nexus_compile_report_latest.json
  else
    echo "[WARN] No latest compiler report found yet."
  fi
}

show_status() {
  echo "[NG] NEXUS GATE STATUS"
  [[ -f state/update_index.v0.1.4.json ]] && cat state/update_index.v0.1.4.json
  [[ -f state/failure_mode_index.v0.1.4.json ]] && cat state/failure_mode_index.v0.1.4.json
  [[ -f state/cold_evidence_index.v0.1.5.json ]] && cat state/cold_evidence_index.v0.1.5.json
  [[ -f reports/nexus_compile_report_latest.json ]] && cat reports/nexus_compile_report_latest.json
  git status --short || true
}

run_loop() {
  local forever="$1"
  local i=0
  while true; do
    i=$((i + 1))
    echo "[NG] Cycle $i"
    run_compiler
    if [[ "$forever" != "1" && "$i" -ge "$cycles" ]]; then
      break
    fi
    sleep "$interval"
  done
}

promote() {
  run_compiler
  status="$(py - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("reports/nexus_compile_report_latest.json").read_text(encoding="utf-8"))
print(data.get("status", "unknown"))
PY
)"
  if [[ "$status" != "pass" ]]; then
    echo "[FAIL] Promotion blocked. Compiler status: $status"
    exit 1
  fi
  if command -v git >/dev/null 2>&1 && [[ "$no_commit" -ne 1 ]]; then
    git add .
    if [[ -n "$(git status --porcelain)" ]]; then
      git commit -m "chore: promote NEXUS GATE compact gated pass"
    fi
  fi
  if command -v git >/dev/null 2>&1 && [[ -n "$tag" ]]; then
    git tag "$tag"
  fi
  echo "[OK] Promotion gate passed."
}

case "$cmd" in
  rehydrate)
    show_rehydration
    run_compiler
    echo "[OK] Rehydration complete."
    ;;
  compile)
    run_compiler
    echo "[OK] Compile passed."
    ;;
  strict)
    bash scripts/nexus_strict_compile.sh
    ;;
  once)
    run_compiler
    echo "[OK] Once passed."
    ;;
  loop)
    run_loop 0
    ;;
  watch)
    run_loop 1
    ;;
  status)
    show_status
    ;;
  promote)
    promote
    ;;
  *)
    echo "[FAIL] Unknown command: $cmd"
    echo "Commands: rehydrate, compile, strict, once, loop, watch, status, promote"
    exit 2
    ;;
esac
