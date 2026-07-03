#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

py() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
    return
  fi
  python "$@"
}

echo "🜂 NEXUS GATE STATUS"
echo "Root: $ROOT"

if [[ -f state/nexus_gate_state.v0.1.0.json ]]; then
  echo
  echo "State:"
  cat state/nexus_gate_state.v0.1.0.json
  echo
fi

if [[ -f reports/nexus_compile_report_latest.json ]]; then
  echo
  echo "Latest compile:"
  py - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("reports/nexus_compile_report_latest.json").read_text(encoding="utf-8"))
print(f"  status: {data.get('status')}")
print(f"  version: {data.get('version')}")
print(f"  generated: {data.get('generated_at_utc')}")
print(f"  duration_ms: {data.get('duration_ms')}")
failed = [gate for gate in data.get("gates", []) if gate.get("status") == "fail"]
print("  failed gates:")
if not failed:
    print("    none")
for gate in failed:
    print(f"    {gate.get('gate')}: {gate.get('message')}")
PY
fi

if command -v git >/dev/null 2>&1; then
  echo
  echo "Git:"
  git status --short
  git log --oneline -5
fi