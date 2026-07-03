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


## Goal Lock / Compression Contract

Before adding code, an agent must check:

```text
docs/goal/GOAL_LOCK.md
docs/runtime/PACKING_AND_COMPRESSION.md
state/goal_lock.v0.1.6.json
```

Do not expand the repo just to expand it. New code must serve one of these NEXUS GATE lanes:

```text
adapter
schema
codec
authority
hot route
cold evidence
wound route
replay
disengagement
ledger
compiler
```

Run before claiming completion:

```powershell
.\scripts\nexus.ps1 pack
```


## Adapter Registry Contract

Before adding a framework integration, the agent must add or inspect:

```text
docs/adapters/ADAPTER_REGISTRY.md
schemas/adapter_manifest.v0.1.7.schema.json
registry/adapters.local_demo.v0.1.7.json
state/adapter_registry_index.v0.1.7.json
nexus_gate/adapters/registry.py
nexus_gate/adapters/local_demo.py
```

Hard rules:

```text
No adapter, no bridge.
No manifest, no registration.
No normalized StatePacket, no route.
No receptor export, no transfer target.
```


## Receptor Registry Contract

Before adding a transfer target, the agent must add or inspect:

```text
docs/receptors/RECEPTOR_REGISTRY.md
schemas/receptor_manifest.v0.1.8.schema.json
registry/receptors.local_demo.v0.1.8.json
state/receptor_registry_index.v0.1.8.json
nexus_gate/receptors/registry.py
nexus_gate/receptors/compatibility.py
```

Hard rules:

```text
No receptor, no transfer target.
No compatibility decision, no engagement.
No unsupported schema, no receptor route.
No unsupported action, no receptor route.
```


## Bridge Session Contract

Before adding a real framework bridge, the agent must inspect:

```text
docs/bridge/BRIDGE_SESSION_RUNNER.md
state/bridge_session_index.v0.1.9.json
nexus_gate/bridge/session.py
reports/nexus_bridge_compile_report_latest.json
```

Hard rules:

```text
No bridge session without adapter normalization.
No bridge session without route decision.
No bridge session without receptor compatibility.
No bridge report without claim boundary.
```


## Bounded Bridge Runtime Contract

Before adding a real external bridge, the agent must inspect:

```text
docs/bridge/BOUNDED_BRIDGE_RUNTIME.md
state/bounded_bridge_runtime_index.v0.2.0.json
nexus_gate/bridge/runtime.py
nexus_gate/bridge/runtime_compiler.py
reports/nexus_bounded_runtime_report_latest.json
```

Hard rules:

```text
No runtime without event limit.
No runtime without bridge session reports.
No runtime without summary counts.
No runtime without claim boundary.
No promotion without runtime compiler pass.
```
