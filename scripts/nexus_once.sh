#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
py() { if command -v python3 >/dev/null 2>&1; then python3 "$@"; else python "$@"; fi; }
echo "🜂 NEXUS GATE one-shot compile starting..."
py -m nexus_gate.compiler --root . --json
echo "✓ NEXUS GATE one-shot compile passed."
