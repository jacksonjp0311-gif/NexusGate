# NEXUS GATE Update Chart

This chart must be visible during rehydration.

## Current Update Chain

| Version | Update | Gate Result | Notes |
|---|---|---|---|
| v0.1.0 | Local scaffold. | prior pass | Base repo skeleton. |
| v0.1.1 | Gated compiler. | partial | Freeze bug in helper path. |
| v0.1.1b | Compiler rescue patch. | pass | Direct compiler wrapper repaired. |
| v0.1.2b | Dual-shell runtime. | failed | Gate mismatch around direct compiler calls. |
| v0.1.2c | Dual-shell gate correction. | superseded | Direct compiler-call rule enforced. |
| v0.1.3d | Portable RHP/Nexus/AI shell. | failed | README omitted exact dual-shell rule required by existing test. |
| v0.1.4 | Rehydration failure/update chart. | wrapper failed | Indented here-string broke PowerShell parsing. |
| v0.1.4b | Safe rehydration failure/update chart. | pass-core | Python compile, tests, compiler, PowerShell rehydrate passed; Bash failed because WSL had no installed distro. |
| v0.1.4c | Compact runtime surface. | pass | Compact PowerShell passed, unusable Bash skipped, committed checkpoint. |
| v0.1.5 | Strict compiler + Cold Evidence | current | Adds cold evidence contracts, wound routing, strict compiler gates, and stricter evidence visibility. |

## Current Required Update Rule

```text
Every version step must update:
1. README current health.
2. failure mode chart.
3. update chart.
4. rehydration manifest.
5. route map if paths changed.
6. tests if gates changed.
7. ledger after validation.
```

## Update Visibility Law

```text
No agent rehydration without update chart visibility.
No version step without update chart entry.
No stale chart after failed validation.
No silent repair after failed validation.
```

Boundary: the update chart improves repository continuity. It does not prove correctness, safety, security, or production readiness.
