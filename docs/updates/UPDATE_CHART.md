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
| v0.1.4b | Safe rehydration failure/update chart. | pass-core | Rehydration chart core pass. |
| v0.1.4c | Compact runtime surface. | pass | Compact command surface and safe Bash detection. |
| v0.1.5 | Strict compiler + Cold Evidence | pass | Adds cold evidence contracts, wound routing, strict compiler gates. |
| v0.1.6b | Compression Rescue + Lineage Restore | pass | Pack compiler and compressed bundle pass. |
| v0.1.7 | Adapter Registry + LocalDemoAdapter | pass | Adds adapter registry, manifest compiler, and first demo adapter. |
| v0.1.8 | Receptor Registry + Compatibility Compiler | pass | Adds receptor manifests, receptor registry, compatibility decisions, and receptor compiler. |
| v0.1.9 | Bridge Session Runner | failed | StatePacket lacked to_dict and compact script dropped FAILURE_MODE_CHART marker. |
| v0.1.9b | Bridge Session Rescue | current | Adds safe packet serialization and restores compact marker visibility. |

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
8. pack manifest if code surface changed.
```

## Update Visibility Law

```text
No agent rehydration without update chart visibility.
No version step without update chart entry.
No stale chart after failed validation.
No silent repair after failed validation.
No growing code surface without pack report.
No lineage row may be deleted while tests still depend on it.
```

Boundary: the update chart improves repository continuity. It does not prove correctness, safety, security, or production readiness.
