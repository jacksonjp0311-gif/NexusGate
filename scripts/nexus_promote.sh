#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
py() { if command -v python3 >/dev/null 2>&1; then python3 "$@"; else python "$@"; fi; }
py -m nexus_gate.compiler --root . --json
git add .
if [[ -n "$(git status --porcelain)" ]]; then git commit -m "chore: promote NEXUS GATE gated pass"; fi
echo "✓ Promotion gate passed."
