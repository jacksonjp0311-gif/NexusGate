# NEXUS GITNEXUS Scope Hygiene v0.3.8

## Purpose

GITNEXUS should not default to a graph polluted by generated runtime artifacts.
The default view is now CORE SCOPE.

## Hidden from default graph view

- reports/
- state/
- ledger/
- compact_compile_logs/
- backup files
- JSONL ledgers
- *_latest.json runtime snapshots
- Tesseract Neural Network memory/state files
- GITNEXUS generated reports/state/ledger
- old GITNEXUS renderer versions
- inactive conversation bridge versions a-e
- test bridge history a-e
- GITNEXUS self-renderer files

## Boundary

This does not delete history. It hides or filters generated/noisy artifacts from
the default GITNEXUS evidence graph. Debug/all-file graph mode can be restored
later as an explicit operator mode.