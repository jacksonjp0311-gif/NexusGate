#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MAX_CYCLES=1
INTERVAL=5
WATCH=0
AUTO_COMMIT=0
STOP_ON_FAIL=0
OPEN_REPORT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-cycles)
      MAX_CYCLES="$2"
      shift 2
      ;;
    --interval)
      INTERVAL="$2"
      shift 2
      ;;
    --watch)
      WATCH=1
      shift
      ;;
    --auto-commit)
      AUTO_COMMIT=1
      shift
      ;;
    --stop-on-fail)
      STOP_ON_FAIL=1
      shift
      ;;
    --open-report)
      OPEN_REPORT=1
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 2
      ;;
  esac
done

py() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
    return
  fi
  python "$@"
}

say() {
  printf '%s %s\n' "$1" "$2"
}

append_log() {
  mkdir -p logs
  printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$1" >> logs/nexus_dev_loop.log
}

run_compiler() {
  mkdir -p logs
  say "🜂" "Running gated compiler."
  append_log "compile_start shell=bash"

  set +e
  py -m nexus_gate.compiler --root . --json 2>&1 | tee logs/nexus_compile_console_latest.log
  code=${PIPESTATUS[0]}
  set -e

  if [[ ! -f reports/nexus_compile_report_latest.json ]]; then
    append_log "compile_no_report shell=bash exit_code=$code"
    return 2
  fi

  status="$(py - <<'PY'
import json
from pathlib import Path
path = Path("reports/nexus_compile_report_latest.json")
data = json.loads(path.read_text(encoding="utf-8"))
print(data.get("status", "unknown"))
PY
)"

  duration="$(py - <<'PY'
import json
from pathlib import Path
path = Path("reports/nexus_compile_report_latest.json")
data = json.loads(path.read_text(encoding="utf-8"))
print(data.get("duration_ms", "unknown"))
PY
)"

  if [[ "$code" -ne 0 ]]; then
    append_log "compile_fail shell=bash exit_code=$code status=$status"
    return "$code"
  fi

  append_log "compile_pass shell=bash duration_ms=$duration"
  return 0
}

commit_clean_pass() {
  if ! command -v git >/dev/null 2>&1; then
    say "∿" "Git not found. Skipping auto-commit."
    return
  fi

  git add .
  if [[ -z "$(git status --porcelain)" ]]; then
    say "✓" "No changes to commit."
    return
  fi

  stamp="$(date -u +"%Y%m%d_%H%M%S")"
  git commit -m "chore: gated dev loop pass $stamp"
  append_log "auto_commit shell=bash"
}

cycle=0

while true; do
  cycle=$((cycle + 1))
  say "🜂" "NEXUS GATE cycle $cycle started."
  append_log "cycle_start shell=bash cycle=$cycle"

  if run_compiler; then
    duration="$(py - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("reports/nexus_compile_report_latest.json").read_text(encoding="utf-8"))
print(data.get("duration_ms", "unknown"))
PY
)"
    say "✓" "Cycle $cycle PASS. Duration: ${duration} ms"

    if [[ "$AUTO_COMMIT" -eq 1 ]]; then
      commit_clean_pass
    fi
  else
    code=$?
    say "⚠" "Cycle $cycle FAIL. Report: reports/nexus_compile_report_latest.json"
    append_log "cycle_fail shell=bash cycle=$cycle exit_code=$code"

    if [[ "$STOP_ON_FAIL" -eq 1 ]]; then
      break
    fi
  fi

  if [[ "$OPEN_REPORT" -eq 1 ]]; then
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open reports/nexus_compile_report_latest.json >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
      open reports/nexus_compile_report_latest.json >/dev/null 2>&1 || true
    fi
  fi

  append_log "cycle_end shell=bash cycle=$cycle"

  if [[ "$WATCH" -ne 1 && "$cycle" -ge "$MAX_CYCLES" ]]; then
    break
  fi

  say "∿" "Sleeping $INTERVAL seconds."
  sleep "$INTERVAL"
done

say "🜂" "NEXUS GATE dev loop complete."