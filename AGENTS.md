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

## Predictive Timing Preflight

Before running full `evolve`, pack, broad test suites, Electron smoke, or any long-running validation lane, run:

```powershell
.\scripts\nexus.ps1 predictive-timing
```

Use the packet at `reports/nexus_predictive_gate_timing_latest.json` to choose the cheapest valid next gate. If runtime pressure is high, prefer targeted tests or the named timing recommendation before repeating an expensive lane.

Hard rules:

```text
Predictive timing is recommendation-only.
It may reduce wasted tokens and wall-clock time.
It may not hide failures, bypass gates, self-authorize, or extend authority.
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
reports/nexus_predictive_gate_timing_latest.json, if present
state/algorithms/nexus_algorithm_cards_latest.json, if present
state/discoveries/nexus_discovery_cards_latest.json, if present
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


## Human Surface Contract

When running NEXUS from PowerShell, prefer:

```powershell
.\scripts\nexus.ps1 human
```

Hard rules:

```text
No operator flood.
No raw JSON wall unless requested.
No CRLF warning noise in normal runs.
No completion claim without compiled report files.
```


## NEXUS v0.2.2 Operator Preference

Use this lane for normal evolution:

```powershell
.\scripts\nexus.ps1 predictive-timing
.\scripts\nexus.ps1 evolve
```

It compiles the code, tests, bridge, runtime, evidence compaction, interconnect graph, feedback report, and pack manifest using the human-readable surface.


## NEXUS v0.2.2b Self-Healing Lane

Use:

```powershell
.\scripts\nexus.ps1 heal
.\scripts\nexus.ps1 evolve
```

Self-healing in this repo means recommendation, dry-run, apply gate, and validation evidence. It does not mean autonomous file writes or autonomous commits.


## NEXUS v0.2.3 AI Feedback Interface

Future AI systems should begin with:

```text
state/ai_feedback_context_latest.json
docs/feedback/FEEDBACK_LOG.md
docs/feedback/FEEDBACK_SYSTEM.md
```

Then run or ask the human to run:

```powershell
.\scripts\nexus.ps1 interface
.\scripts\nexus.ps1 evolve
```

Do not assume autonomous write authority. Use feedback as recommendation/dry-run/apply-gate evidence.


## NEXUS v0.2.4b PowerShell HUD TUI

Use this as the primary human/AI debug loop:

```powershell
.\scripts\nexus.ps1 tui
```

Use `/ai` inside the TUI to print a copyable handoff block for ChatGPT/Codex.

## NEXUS v0.2.6 AI Agent Interconnection

The interconnect graph now includes governed AI/operator process nodes for the Codex/ChatGPT handoff loop, TUI exports, feedback context, feedback log, operator packets, and return-to-operator recommendations.

Hard rules:

```text
No AI handoff without feedback context.
No autonomous self-authorization.
No UI bypass of compiler/evolve gates.
AI process context is recommendation evidence, not authority.
```

## NEXUS v0.2.7 Domain Interconnection Profiles

The interconnect graph now declares CLI formatting, bio, chem, coding, and neural domain profile nodes.

Use the TUI command:

```powershell
/domains
```

Hard rules:

```text
Domain routing is not domain validation.
No biological claim without source metadata and validation evidence.
No chemical claim without structure identifier and provenance.
No code-tool route without machine-readable contract or diagnostics evidence.
No neural route without model format, runtime boundary, and evidence report.
```

## NEXUS v0.2.8 TUI Interconnect Console

Use this inside the TUI:

```powershell
/graph
```

or:

```powershell
/interconnect
```

The view is read-only evidence orientation. It must not mutate graph state, bypass evolve, or treat graph visibility as proof.

## NEXUS v0.2.9 TUI Snapshot Bridge

Use this inside the TUI:

```powershell
/snapshot
```

The generated HTML snapshot includes graph status, node and edge counts, checks, placeholder evidence paths, feedback health, next action, and bridge surfaces.

Hard rule:

```text
Snapshot visibility is not authority, proof, or validation.
```

## NEXUS v0.3.0 TUI Surface State

Use this inside the TUI:

```powershell
/surface
```

It writes:

```text
reports/tui/nexus_tui_surface_latest.json
```

The file is a read-only state summary for Electron/dashboard consumers. It is not authority, proof, or a shell execution surface.

## NEXUS v0.3.1 TUI Snapshot Surface Pair

Use this inside the TUI:

```powershell
/snapshot
```

It writes both:

```text
reports/tui/nexus_tui_snapshot_latest.html
reports/tui/nexus_tui_surface_latest.json
```

The paired export gives future Electron/dashboard consumers a human-readable view and a machine-readable state view from one governed operator action. It remains read-only evidence orientation, not authority or validation proof.

## NEXUS v0.3.2 Electron Read Contract

Before building an Electron surface, inspect:

```text
docs/ui/ELECTRON_READ_CONTRACT.md
state/electron_read_contract_index.v0.3.2.json
tests/test_electron_read_contract.py
```

Electron/dashboard surfaces may read declared evidence files and request only allowlisted NEXUS lanes. They must not run arbitrary shell commands, mutate graph state, bypass evolve, access secrets, write external APIs, self-authorize, or claim validation proof.

## NEXUS v0.3.3 Electron Shell Scaffold

The Electron scaffold lives under:

```text
electron/
docs/ui/ELECTRON_SHELL_SCAFFOLD.md
state/electron_shell_scaffold_index.v0.3.3.json
tests/test_electron_shell_scaffold.py
```

It is installed locally with a committed lockfile, but it is not packaged or production validated. It must remain presentation-only, use context isolation, keep Node integration disabled, run IPC through allowlists, and use the existing NEXUS lanes instead of owning logic.

## NEXUS v0.3.4 Electron Preflight Compiler

Use:

```powershell
.\scripts\nexus.ps1 electron-preflight
```

It writes:

```text
reports/nexus_electron_preflight_report_latest.json
```

The preflight compiler verifies the Electron scaffold contract and guardrails. It does not install dependencies, package the desktop app, launch Electron, grant shell authority, or authorize autonomous action.

## NEXUS v0.3.7 Reflective Intelligence Gateway

Before evolving reflective or interface surfaces, inspect:

```text
docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md
docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md
docs/intelligence/REPO_NATIVE_LEARNING.md
docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md
docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md
docs/interfaces/INTERFACE_ADAPTER_CONTRACT.md
docs/versioning/NEXUS_LINEAGE_PROTOCOL.md
state/interface_adapter_contract_index.v0.3.7.json
state/nexus_lineage_manifest_latest.json
reports/nexus_reflective_loop_report_latest.json
reports/nexus_domain_intelligence_report_latest.json
```

Use:

```powershell
.\scripts\nexus.ps1 reflect
.\scripts\nexus.ps1 domain
.\scripts\nexus.ps1 evolve
```

Hard rules:

```text
Reflective intelligence is permitted.
Autonomous authority is not.
Organic evolution is allowed.
Ungated compounding is not.
No reflective loop without evidence surfaces.
No interface adapter may declare autonomous mutation authority.
```

## NEXUS v0.4.0 Domain Intelligence Orchestrator

Before creating or promoting domain claims, inspect:

```text
docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md
docs/intelligence/REPO_NATIVE_LEARNING.md
docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md
docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md
state/domain_intelligence_index.v0.4.0.json
state/repo_native_learning_index.v0.4.0.json
state/codex_orchestration_index.v0.4.0.json
reports/nexus_domain_intelligence_report_latest.json
domains/
```

Use:

```powershell
.\scripts\nexus.ps1 domain
.\scripts\nexus.ps1 reflect
.\scripts\nexus.ps1 evolve
```

Hard rules:

```text
Repo-native learning is allowed.
Autonomous authority is not.
Cross-domain synthesis is allowed.
Unsupported claims are not.
No simulation becomes real-world proof.
No code demo becomes production validation.
No biological pattern becomes medical advice.
No mathematical conjecture becomes theorem without proof.
```

## NEXUS v0.5.1 Reflective Neural Assembly Chat Distribution

Before evolving Codex, ChatGPT, local-agent, or neural assembly handoff behavior, inspect:

```text
labs/reflective_neural_assembly/MINI_README.md
labs/reflective_neural_assembly/CHAT_INTELLIGENCE_DISTRIBUTION.md
labs/reflective_neural_assembly/state/chat_intelligence_distribution_index.v0.5.1.json
labs/reflective_neural_assembly/reports/neural_assembly_report_latest.json
labs/reflective_neural_assembly/reports/neural_intelligence_distribution_latest.json
labs/reflective_neural_assembly/handoffs/
```

Use:

```powershell
python .\labs\reflective_neural_assembly\run_neural_assembly.py --intent "What should we do next?"
python -m unittest discover -s labs/reflective_neural_assembly/tests
```

Hard rules:

```text
Distribute intelligence.
Do not distribute authority.
No chat handoff may self-authorize.
No neural lab may execute arbitrary shell.
No neural lab may mutate the parent repo.
No neural lab may write external APIs.
No compressed handoff is proof of correctness, safety, security, production readiness, or truth.
```

## NEXUS v1.1.2 Phi Gate Supervisor Compiler Seal

Before evolving Phi gate supervision or model-assisted repair lanes, inspect:

```text
docs/runtime/NEXUS_PHI_GATE_SUPERVISOR.md
nexus_gate/loops/phi_gate_supervisor.py
nexus_gate/loops/phi_gate_supervisor_compile.py
state/loops/nexus_phi_gate_supervisor.v1.1.1.json
reports/nexus_phi_gate_supervisor_report_latest.json
```

Use:

```powershell
.\scripts\nexus.ps1 phi-gate-compile
.\scripts\nexus.ps1 phi-gate -Gate ci-core
```

Hard rules:

```text
Phi may advise; Nexus verifies; human authorizes durable mutation.
Command surfaces must use --call-model and --auto-repair.
Legacy --call-phi and --self-heal flags are contract failures.
No supervisor path may grant arbitrary shell, git push, network, secret, or autonomous mutation authority.
```
