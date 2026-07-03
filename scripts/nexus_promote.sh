#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TAG=""
NO_COMMIT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      TAG="$2"
      shift 2
      ;;
    --no-commit)
      NO_COMMIT=1
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

echo "🜂 Running promotion gate."

bash scripts/nexus_once.sh

if [[ ! -f reports/nexus_compile_report_latest.json ]]; then
  echo "Latest compile report missing."
  exit 1
fi

status="$(py - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("reports/nexus_compile_report_latest.json").read_text(encoding="utf-8"))
print(data.get("status", "unknown"))
PY
)"

if [[ "$status" != "pass" ]]; then
  echo "Promotion blocked. Compiler status: $status"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "∿ Git not found. Promotion gate passed without Git checkpoint."
  exit 0
fi

if [[ "$NO_COMMIT" -ne 1 ]]; then
  git add .
  if [[ -n "$(git status --porcelain)" ]]; then
    stamp="$(date -u +"%Y%m%d_%H%M%S")"
    git commit -m "chore: promote NEXUS GATE gated pass $stamp"
  fi
fi

if [[ -n "$TAG" ]]; then
  git tag "$TAG"
  echo "✓ Tag created: $TAG"
fi

echo "✓ Promotion gate passed."