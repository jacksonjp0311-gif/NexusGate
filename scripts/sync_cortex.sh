#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-${HOME}/OneDrive/Desktop/Cortex}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/Cortex"
REPORTS="${ROOT}/reports"

mkdir -p "${TARGET}" "${REPORTS}"

rsync -a \
  --exclude '.git' \
  --exclude '.cortex' \
  --exclude '.pytest_cache' \
  --exclude '.ruff_cache' \
  --exclude '__pycache__' \
  --exclude 'build' \
  --exclude 'work' \
  --exclude 'cortex_memory.egg-info' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '.coverage' \
  "${SOURCE}/" "${TARGET}/"

SOURCE_COMMIT="unknown"
if git -C "${SOURCE}" rev-parse --short HEAD >/dev/null 2>&1; then
  SOURCE_COMMIT="$(git -C "${SOURCE}" rev-parse --short HEAD)"
fi

python - "$SOURCE" "$TARGET" "$SOURCE_COMMIT" "$REPORTS" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

source, target, source_commit, reports = sys.argv[1:5]
payload = {
    "system": "NEXUS GATE",
    "lane": "sync-cortex",
    "status": "pass",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": source,
    "target": target,
    "source_commit": source_commit,
    "copied_surface": "Cortex source/docs/tests/benchmarks only",
    "excluded_dirs": [".git", ".cortex", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "work", "cortex_memory.egg-info"],
    "excluded_files": ["*.pyc", "*.pyo", ".coverage"],
    "authority_boundary": "Cortex sync copies local source artifacts only. It does not import upstream git history, runtime memory, secrets, caches, external APIs, or grant Cortex mutation authority.",
    "next_action": "./scripts/nexus.sh cortex",
}
reports_path = Path(reports)
(reports_path / "nexus_cortex_sync_report_latest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
(reports_path / f"nexus_cortex_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
PY
