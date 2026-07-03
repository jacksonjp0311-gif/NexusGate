# AGENTS.md — NEXUS GATE Agent Operating Contract

## Entry Order

1. Read `README.md`.
2. Read `docs/context/repository_context_index.json`.
3. Read `docs/context/rcc_nexus_index.json`.
4. Read `docs/context/validation_surface.md`.
5. Read `rcc/nexus/route_map.json`.
6. Read the mini README in the target folder.
7. Inspect relevant source/tests/docs only.
8. Patch the smallest necessary surface.
9. Run the gated compiler.
10. Update docs/context/route maps if repository geometry changed.

## Non-Claim Lock

Do not claim production validation, safety proof, security proof, correctness proof, autonomous authority, or tool authority.

## Required Gate

```powershell
python -m nexus_gate.compiler --root . --json
```


## Rehydration Visibility Contract

Before patching, every agent must read:

```text
docs/context/REHYDRATION_BOOT.md
docs/context/rehydration_manifest.v0.1.4.json
docs/failure_modes/FAILURE_MODE_CHART.md
docs/updates/UPDATE_CHART.md
state/failure_mode_index.v0.1.4.json
state/update_index.v0.1.4.json
reports/nexus_compile_report_latest.json, if present
```

Hard rule:

```text
No rehydration without failure/update visibility.
```


## Cold Evidence / Wound Routing Contract

Before trusting a previously failed route, the agent must check:

```text
docs/evidence/COLD_EVIDENCE_ENGINE.md
docs/failure_modes/WOUND_ROUTING.md
state/cold_evidence_index.v0.1.5.json
reports/nexus_compile_report_latest.json
```

Hard rules:

```text
No shadow failure without wound route.
No re-engagement without replay certificate.
No specialist promotion without cold evidence.
```
