#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "🜂 NEXUS GATE STATUS"
[[ -f state/nexus_gate_state.v0.1.3.json ]] && cat state/nexus_gate_state.v0.1.3.json
[[ -f reports/nexus_compile_report_latest.json ]] && cat reports/nexus_compile_report_latest.json
git status --short || true
