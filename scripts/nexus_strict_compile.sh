#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

py() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    python "$@"
  fi
}

echo "[NG] Strict compile: Python compile"
py -m compileall nexus_gate tests

echo "[NG] Strict compile: unit tests"
py -m unittest discover -s tests

echo "[NG] Strict compile: NEXUS compiler"
py -m nexus_gate.compiler --root . --json

echo "[NG] Strict compile: compact rehydration"
bash scripts/nexus.sh rehydrate

echo "[OK] Strict compiler passed."
