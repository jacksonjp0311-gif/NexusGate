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

echo "[NG] NEXUS GATE REHYDRATION BOOT"
echo "[NG] Required read order:"
echo "  1. README.md"
echo "  2. docs/context/REHYDRATION_BOOT.md"
echo "  3. docs/context/rehydration_manifest.v0.1.4.json"
echo "  4. docs/failure_modes/FAILURE_MODE_CHART.md"
echo "  5. docs/updates/UPDATE_CHART.md"
echo "  6. state/failure_mode_index.v0.1.4.json"
echo "  7. state/update_index.v0.1.4.json"
echo "  8. reports/nexus_compile_report_latest.json, if present"
echo "  9. rcc/nexus/route_map.json"
echo "  10. target folder README.md"

echo
echo "[NG] Failure chart:"
sed -n '1,80p' docs/failure_modes/FAILURE_MODE_CHART.md

echo
echo "[NG] Update chart:"
sed -n '1,80p' docs/updates/UPDATE_CHART.md

echo
if [[ -f reports/nexus_compile_report_latest.json ]]; then
  echo "[NG] Latest compiler report:"
  cat reports/nexus_compile_report_latest.json
else
  echo "[WARN] No latest compiler report found yet."
fi

echo
echo "[NG] Running gated compiler after rehydration visibility..."
py -m nexus_gate.compiler --root . --json
echo "[OK] Rehydration boot complete."
