#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD="${1:-cell}"
shift || true
case "$CMD" in
  cell|cell-doctor) python -m nexus_gate.nexus_cell.cli doctor --root "$ROOT" "$@" ;;
  cell-run) python -m nexus_gate.nexus_cell.cli run --root "$ROOT" --runner mock --payload "$ROOT/NexusCell/examples/hello.ps1" "$@" ;;
  cell-ledger) python -m nexus_gate.nexus_cell.cli ledger --root "$ROOT" "$@" ;;
  cell-policy) python -m nexus_gate.nexus_cell.cli policy --root "$ROOT" "$@" ;;
  *) echo "Unknown NexusCell command: $CMD" >&2; exit 2 ;;
esac
