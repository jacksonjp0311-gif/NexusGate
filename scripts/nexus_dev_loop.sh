#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MAX_CYCLES=1
INTERVAL=5
WATCH=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-cycles) MAX_CYCLES="$2"; shift 2 ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --watch) WATCH=1; shift ;;
    *) echo "Unknown argument: $1"; exit 2 ;;
  esac
done
py() { if command -v python3 >/dev/null 2>&1; then python3 "$@"; else python "$@"; fi; }
cycle=0
while true; do
  cycle=$((cycle + 1))
  echo "🜂 NEXUS GATE cycle $cycle"
  py -m nexus_gate.compiler --root . --json
  echo "✓ Cycle passed."
  if [[ "$WATCH" -ne 1 && "$cycle" -ge "$MAX_CYCLES" ]]; then break; fi
  sleep "$INTERVAL"
done
