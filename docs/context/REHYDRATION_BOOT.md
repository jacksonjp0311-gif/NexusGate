# NEXUS GATE Rehydration Boot

This document defines what a human or AI agent must see before editing the repository.

## Required Rehydration Sequence

```text
Anchor repository root
  -> read README.md
  -> read docs/context/REHYDRATION_BOOT.md
  -> read docs/context/rehydration_manifest.v0.1.4.json
  -> read docs/failure_modes/FAILURE_MODE_CHART.md
  -> read docs/updates/UPDATE_CHART.md
  -> read state/failure_mode_index.v0.1.4.json
  -> read state/update_index.v0.1.4.json
  -> read reports/nexus_compile_report_latest.json if present
  -> read rcc/nexus/route_map.json
  -> read target folder README.md
  -> inspect relevant source/tests/docs
  -> patch smallest surface
  -> run gated compiler
```

## Agent Must See

| Surface | Why |
|---|---|
| Failure chart | Prevents repeating known failure patterns. |
| Update chart | Preserves version continuity. |
| Latest compiler report | Shows current gate status. |
| Route map | Prevents blind navigation. |
| Target mini README | Preserves local context. |

## Hard Rule

```text
No rehydration without failure/update visibility.
```

Boundary: rehydration boot improves orientation. It does not prove correctness, security, safety, or production readiness.
