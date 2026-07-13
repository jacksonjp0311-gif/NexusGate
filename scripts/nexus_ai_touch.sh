#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMMAND="${1:-status}"
shift || true
case "$COMMAND" in
  begin) python -m nexus_gate.intelligence.cli touch-begin --root . --provider "${PROVIDER:-codex}" --session-id "${SESSION_ID:-manual}" --intent "${*:-${TAG:-Declared AI touch session.}}" --json ;;
  status) python -m nexus_gate.intelligence.cli touch-status --root . --interaction-id "${INTERACTION_ID:-}" --json ;;
  end) python -m nexus_gate.intelligence.cli touch-end --root . --interaction-id "${INTERACTION_ID:-${1:-}}" --disposition "${DISPOSITION:-pending_review}" --json ;;
  abort) python -m nexus_gate.intelligence.cli touch-abort --root . --interaction-id "${INTERACTION_ID:-${1:-}}" --json ;;
  verify) python -m nexus_gate.intelligence.cli touch-verify --root . --interaction-id "${INTERACTION_ID:-}" --json ;;
  list) python -m nexus_gate.intelligence.cli touch-list --root . --json ;;
  replay-verify) python -m nexus_gate.intelligence.cli touch-replay-verify --root . --json ;;
  *) echo "Unknown ai-touch command: $COMMAND" >&2; exit 2 ;;
esac
