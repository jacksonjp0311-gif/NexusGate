# NEXUS GATE
**Reflective Intelligence Layer for AI Systems**
NEXUS GATE is a local-first reflective intelligence layer for AI systems: a governed transfer boundary where model output, local tools, repo evidence, runtime reports, and human authorization meet. The portal is only the doorway; NEXUS GATE is the reflective system behind it, keeping AI work observable, diagnosable, bounded, oriented, and evidence-governed without granting autonomous authority. It turns reasoning into durable artifacts, gates those artifacts, and rehydrates the next human/AI session from the evidence that survived.

## Capability Surface
- Operator HUDs: Electron, PowerShell TUI, Spiral Core Portal, Dev Mode / HANDOFF, Mode Selection, and System Monitor.
- Governed lanes: `status`, `evolve`, `origin-seal`, `decision-envelope`, `coherence-field`, `reflect`, `domain`, `toolbelt`, `preflight`, `predictive-timing`, `predictive-evolve`, `predictive-memory`, `certificate-resume`, `cortex-refresh`, `wound-compress`, `phi-wound`, `phi-loop-auto`, and `phi-gate-auto`.
- Intelligence loops: AI-callable local loop fabric, Algorithm Cards, Discovery Cards, v0.9.3 AI Loop Toolkit Expansion, v0.9.4 Personal Coding Paradise, Toolbelt Console Integration, v0.9.8 Wound Compression Engine, v0.9.9 Preflight Optimizer, v1.1.0 Phi Microdose Loop, AI Toolbelt Console, Toolbelt Cockpit Output, and Meta-Orchestrator Gate.
- Evidence organs: Neural Activity visual organ, GITNEXUS local codegraph, PetriDishPortal, NexusCell containment, feedback ledger, handoff packets, and compiler reports.
- Guardrails: human-authorized mutation only, no autonomous authority, no bypassing gates, no production/safety/security proof claims from local passes.
- Lineage is preserved in docs/versioning, docs/runtime, reports, and the compatibility marker bank below instead of a bulky README seal list.

```text
human intent -> origin alignment -> route/authority gate -> evidence -> human-authorized durable mutation
```

## Start Here
```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate"
.\scripts\nexus.ps1 toolbelt
.\scripts\nexus.ps1 toolbelt-next -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-json -Tag "<intent>"
.\scripts\nexus.ps1 origin-seal
.\scripts\nexus.ps1 decision-envelope
.\scripts\nexus.ps1 coherence-field
.\scripts\nexus.ps1 wound-compress -Tag "<failed gate>"
.\scripts\nexus.ps1 preflight -Tag "<intent>"
python -m unittest discover -s tests
python -m nexus_gate.compiler --root . --json
```

## Human Director Box
NEXUS GATE current line: v2.1.0 Causal Coherence Routing. Product identity is bound by `state/nexus_origin_manifest_latest.json` and `reports/nexus_origin_seal_latest.json`; Decision Envelope now consumes `reports/nexus_coherence_field_latest.json` through a recommendation arbiter. Older version strings in `pyproject.toml`, `nexus_gate/__init__.py`, lineage files, and subsystem reports are preserved as subsystem lineage until a deliberate compatibility migration updates them. Toolbelt, Preflight, Wound Compression, Predictive Memory, Cortex Refresh, Origin Seal, Decision Envelope, and Coherence Field compile into recommendation-only route evidence for Codex/chat/Electron HUD rehydration; authority remains human-bound.

## Priority Discovery: Predictive Gate Timing
Predictive Gate Timing / Runtime Pressure Model is a priority. Timeout history is not intelligence by itself, but recorded lane duration, timeout budget, pass/fail state, artifact churn, and repo size can become bounded expectation: baseline -> drift -> anomaly -> recommended next timeout. The model may predict runtime pressure and recommend gate budgets; it may not bypass gates, hide failures, or self-authorize mutation.

Predictive Evolve is the dry-run planner built on that discovery: predictive timing -> scope classification -> gate selection -> dry-run plan -> final evolve seal required. `.\scripts\nexus.ps1 predictive-memory` fuses Cortex memory health, vector benchmarks, Algorithm Cards, Discovery Cards, and predictive evolve into a memory-aware recommendation plus trend row; it may recommend, not execute or replace final `evolve`.

Certificate Resume v0.1 records passed-gate evidence hashes from the latest human-surface run and recommends a resume point after failure. Certificates are not a pass claim by themselves; `.\scripts\nexus.ps1 evolve` remains the final commit seal.

## Self-Bootstrap / Coherence Field
`.\scripts\nexus.ps1 decision-envelope` compiles origin -> memory -> runtime pressure -> wounds -> certificates -> git scope -> selected next action; `.\scripts\nexus.ps1 coherence-field` compiles the field packet into coherence score, lineage entropy, selected action, and continuity status. In v2.1 the arbiter lets coherence steer recommendations; it may not execute, self-authorize, mutate the repo, grant authority, or replace final `evolve`.

## Cortex
Cortex is imported at `Cortex/` as a recommendation-only repository assimilation and selective-memory organ. Sync upgrades from the standalone repo with `.\scripts\nexus.ps1 sync-cortex -Tag "C:\Users\jacks\OneDrive\Desktop\Cortex"`; current synced source is upstream commit `8d5e60b`. The vector storage upgrade migrated `7,919` NEXUS Cortex vectors to versioned float32 BLOBs, reducing benchmark vector payload by `34.71%` and moving sample query mean from `242.630 ms` legacy to `183.011 ms` blob. See `docs/runtime/NEXUS_CORTEX.md`, `reports/nexus_cortex_sync_report_latest.json`, and `reports/nexus_cortex_gate_latest.json`.
## AI Toolbelt Console
Use the AI Toolbelt Console before choosing a patch path.
```powershell
.\scripts\nexus.ps1 toolbelt
.\scripts\nexus.ps1 toolbelt-start -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-dashboard -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-next -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-ship -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-json -Tag "<intent>"
```

## Toolbelt Cockpit Output
`toolbelt` prints the readable cockpit. `toolbelt-json` prints the v0.9.7 machine packet. Required packet fields include `next_command`, `recommended_next_command`, `recommended_next_loop`, `repo_status`, `process_chains`, and boundary flags.

Core chains:
```text
Start: toolbelt-start -> toolbelt-dashboard -> next-action-router
Build: idea-forge -> architecture-sketch -> patch-plan -> test-strategy
Debug: debug-lens -> wound-indexed-resume -> compiler-wound-focus
Ship: scope-hygiene -> boundary-scan -> release-brief -> release-seal
Continuity: handoff-pack -> session-brief -> memory-anchor -> continuity-seal
```

## Personal Coding Paradise
v0.9.4 Personal Coding Paradise supplies idea forge, architecture sketch, patch plan, test strategy, debug lens, refactor map, UI polish, docs weaving, memory anchor, command palette, local oracle, continuity seal, creative build chain, debug recovery chain, and safe ship chain.

## AI Loop Toolkit
v0.9.3 AI Loop Toolkit Expansion gives repo radar, scope hygiene, claim-boundary audit, surface map, stale scan, next-action router, handoff pack, dependency preflight, alignment score, boundary scan, release brief, and evolution radar.

## Wound Compression Engine
v0.9.8 compresses bounded-test, compiler, Toolbelt, and git-status evidence into one active-wound packet before the next closer is written.

```text
stdout = smoke only
files = evidence
tail = never truth
passed gates = certificates
active wound = one repair target
```

```powershell
.\scripts\nexus.ps1 wound-compress -Tag "<failed gate>"
```

## Preflight Optimizer
v0.9.9 checks the next mutation surface before a closer runs: command parity, packet contracts, README current-line freshness, bounded-report shape, and ignored-file staging risk.

```powershell
.\scripts\nexus.ps1 preflight -Tag "<intent>"
.\scripts\nexus.ps1 preflight-json -Tag "<intent>"
```

## Phi Wound Advisor
v1.0.0 Phi Wound Advisor adds `phi-wound` and `phi-wound-gpu`: Phi recommends, NexusGate verifies, human authorizes durable mutation.
## Lessons From the v0.9.1 Seal
```text
Gates are certificates.
Do not rerun passed gates unless their inputs changed.
Only heal the active wound.
Patch the smallest surface that can close the wound.
Compile before trust.
Targeted tests prove the wound closed.
Full bounded tests prove no known contract regressed.
The Nexus compiler is the final local seal.
Stage intended files only.
```

Before any future generated script changes this repo, read `chatgpt/scripts.md`.

## RHP Origin Alignment
```text
No RHP alignment, no durable mutation. No mini README, no blind patching. Every new runtime loop must exist in both PowerShell and Bash. No rehydration without failure chart visibility.
```

## AI Operating Contract
```text
Every generated closer should print or write a compact state packet. stage_policy = intended files only. human_authorized_only. Do not stage unrelated runtime residue.
```

## Failure Modes
```text
No adapter, no bridge. No schema, no route. No authority verification, no mutation. No wound route, no retrust. No ledger stub, no compounding. No compile pass, no promotion. No shadow failure without wound route.
```

## GitHub / README / Docs
The Desktop Entry Portal includes a GitHub / README / Docs submenu. Current operator surfaces include Spiral Core Desktop Portal, Electron HUD, PowerShell TUI, Dev Mode / HANDOFF, Failure Doctor, T3MP3ST, Mode Selection HUD, NexusCell, Neural Activity, Nexus Loops / Cards, Algorithm Cards, Discovery Cards, PetriDishPortal, Personal Coding Paradise, AI Toolbelt Console, and Toolbelt Cockpit.

## Phi Wound Ollama Adapter
v1.0.1 routes `phi-wound-gpu` through the non-interactive Ollama JSON adapter instead of the Orange human launcher.
## Documentation Map
| Need | File |
|---|---|
| 90-second intro | `README_90_SECONDS.md` |
| Entrypoints | `docs/ENTRYPOINTS.md` |
| Docs index | `docs/README.md` |
| Runtime commands | `docs/runtime/` |
| AI Loop Fabric | `docs/runtime/NEXUS_AI_LOOP_FABRIC.md` |
| AI Loop Toolkit | `docs/runtime/NEXUS_AI_LOOP_TOOLKIT.md` |
| AI Toolbelt | `docs/runtime/NEXUS_AI_TOOLBELT.md` |
| Toolbelt Console | `docs/runtime/NEXUS_TOOLBELT_CONSOLE.md` |
| Toolbelt Cockpit | `docs/runtime/NEXUS_TOOLBELT_COCKPIT.md` |
| Wound Compression Engine | `docs/runtime/NEXUS_WOUND_COMPRESSION_ENGINE.md` |
| Phi Wound Advisor | `docs/runtime/NEXUS_PHI_WOUND_ADVISOR.md` |
| Phi Ollama Adapter | `docs/runtime/NEXUS_PHI_WOUND_OLLAMA_ADAPTER.md` |
| Preflight Optimizer | `docs/runtime/NEXUS_PREFLIGHT_OPTIMIZER.md` |
| Predictive Gate Timing | `docs/runtime/NEXUS_PREDICTIVE_GATE_TIMING.md` |
| Predictive Evolve | `docs/runtime/NEXUS_PREDICTIVE_EVOLVE.md` |
| Predictive Memory Orchestrator | `docs/runtime/NEXUS_PREDICTIVE_MEMORY_ORCHESTRATOR.md` |
| Certificate Resume | `docs/runtime/NEXUS_CERTIFICATE_RESUME.md` |
| Cortex | `docs/runtime/NEXUS_CORTEX.md` |
| Algorithm Cards | `docs/runtime/NEXUS_ALGORITHM_CARDS.md` |
| Discovery Cards | `docs/runtime/NEXUS_DISCOVERY_CARDS.md` |
| Meta-Orchestrator Gate | `docs/runtime/NEXUS_META_ORCHESTRATOR_GATE.md` |
| NEXUS Loop Cards | `docs/runtime/NEXUS_LOOP_CARDS.md` |
| PetriDishPortal | `docs/runtime/NEXUS_PETRIDISH_PORTAL.md` |
| Wound-indexed resume loop | `docs/runtime/NEXUS_WOUND_INDEXED_RESUME_LOOP.md` |
| NexusCell | `docs/nexus_cell/NEXUS_CELL.md` |
| GITNEXUS impact bridge | `docs/gitnexus/NEXUS_GITNEXUS_IMPACT_BRIDGE.md` |
| Geometric memory router | `docs/intelligence/NEXUS_GEOMETRIC_MEMORY_ROUTER.md` |
| Geometry manifest | `state/nexus_geometric_memory_manifest.v0.8.3.json` |
| ChatGPT scripting doctrine | `chatgpt/scripts.md` |

## PART I - Human README
NEXUS GATE is a governed local operator workbench for testing whether AI/runtime events can be normalized, routed, blocked, reflected, diagnosed, and preserved as evidence without giving autonomous authority to tools or model output.

## PART II - RHP Nexus README
RHP keeps repository origin, session state, evidence, update charts, failure charts, and compiler visibility aligned before compounding.

## PART III - AI Agent README
AI agents may recommend named local loops, read evidence packets, and draft patches. They may not self-authorize mutation, bypass gates, claim safety proof, or convert model output into repo authority.

## Wound-Indexed Resume Loop
```text
Passed gates are certificates. Later failures become active wounds. Resume from the failed gate unless a passed gate input changed. stdout = smoke only. files = evidence. tail = never truth.
```

<!-- NEXUS:README_MARKER_BANK:BEGIN -->
## Compatibility Marker Bank
Legacy README markers: ## AI Toolbelt ; ## NEXUS Connective Point ; --nexus-neural-embed-scale ; .\\scripts\\nexus.ps1 domain ; .\\scripts\\nexus.ps1 evolve ; .\\scripts\\nexus.ps1 reflect ; .\scripts\nexus.ps1 domain ; .\scripts\nexus.ps1 evolve ; .\scripts\nexus.ps1 reflect ; 8. Failure Modes / Doctor ; AA is the canonical architecture ; AI Toolbelt Console ; AI-callable local loop fabric ; AUTHORITY IS EARNED. ACCESS IS EVIDENCE. ; authority_unverified ; Before any future generated script changes this repo, read `chatgpt/scripts.md`. ; blue/light-blue Spiral Core Portal ; cannot self-authorize ; Canonical status: v0.1.1 visual organ ; commit only when authorized ; compiler_failed ; conjecture ; contextBridge.exposeInMainWorld("nexus" ; cyber ice-blue gateway for human + AI intelligence flow ; dimensional ; embed ; Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass. ; Every new runtime loop must exist in both PowerShell and Bash. ; Failure Intelligence Distributor ; Failure Modes / Doctor Gateway ; FAILURE_MODE_CHART ; Flow: portal -> surface -> evidence -> gate -> durable commit. ; function Invoke-NexusToolbelt",ps); self.assertIn("toolbelt|toolbelt-dashboard",sh); self.assertIn("AI Toolbelt Console ; future systems can continue without chat context ; Gates are certificates. ; geo-clean ; Geometric Memory Router ; getContract ; GitHub / README / Docs ; HUD panel = live embedded Neural Cathedral preview ; human-readable, AI-parsable, and troubleshootable ; Intent -> Evidence -> Authority -> Context ; Invoke-NexusCellExecutionGateConsole ; Invoke-NexusNeuralActivity ; Invoke-NexusShellConsole ; LFTE depth typing + EIMT drift gate + RCMA latent remap + TRAT attractor score ; local-first reflective intelligence layer for AI systems ; N E X U S   G A T E ; Neural Activity ; Neural Activity = visual organ. ; Neural Activity v0.1.1 ; NEXUS GATE :: DESKTOP ENTRY PORTAL ; NEXUS GATE :: SPIRAL CORE PORTAL ; NEXUS Loop Cards ; Nexus Loops / Cards ; NEXUS_FUTURE_SYSTEM_REHYDRATION_HANDOFF.md ; nexus_gate.compiler ; nexus_geometric_memory_manifest.v0.8.3.json ; NEXUS_GEOMETRIC_MEMORY_ROUTER.md ; NEXUS_NEURAL_ACTIVITY_V011_EMBED_KNOBS ; NEXUS_SPIRAL_CORE_ASCII_BEGIN ; NEXUS_SPIRAL_CORE_ASCII_END ; No chat context required ; No mini README, no blind patching. ; No patch without update chart visibility. ; No rehydration without failure chart visibility. ; No RHP alignment, no durable mutation. ; not medical authority ; observable, diagnosable, bounded ; Only heal the active wound. ; PART III - AI Agent README ; production readiness ; push only when authorized ; python -m nexus_gate.geometric_memory.router ; RCC Nexus Echo Location ; readSurface ; Reflective Intelligence Layer for AI Systems ; Reflective Local Loop ; Rehydrate before patching. ; repository evidence wins ; Rule: models recommend; human authorizes durable mutation. ; runLane ; S P I R A L   C O R E   P O R T A L ; schema_missing ; simulation ; Spiral Core Desktop Portal ; Spiral Core Portal v0.1.2 ; surfaceExists ; surrogate previews = deprecated ; tests ; The gate does not give intelligence authority. ; The gate gives authority a visible path through intelligence. ; The portal is only the doorway ; The repository is the origin ; theorem ; Toolbelt Cockpit Output ; toolbelt-dashboard ; toolbelt-json ; toolbelt-start ; unsafe wet-lab ; UPDATE_CHART ; v0.1.1 Canonical Visual Organ ; v0.8.1 UI cleanup line ; v0.8.3F geo preflight cleanup and warning seal line ; v0.9.3 AI Loop Toolkit Expansion ; v0.9.4 Personal Coding Paradise ; WE DO NOT OBEY CHAOS. WE GOVERN THRESHOLDS. ; | ChatGPT scripting doctrine | `chatgpt/scripts.md` | ; | Neural Activity | Canonical visual organ ; | Spiral Core Desktop Portal |
<!-- NEXUS:README_MARKER_BANK:END -->

<!-- NEXUS:README_023N_FRESHNESS_BEGIN -->
## Current Portal and Freshness Surface
Spiral Core Desktop Portal is the current desktop operator surface. The active portal is the blue/light-blue Spiral Core Portal. Neural Activity v0.1.1 remains the canonical visual organ. Spiral Core Portal v0.1.2 remains the current portal line. Neural Activity = visual organ.
## Legacy Compatibility Marker Bank
Reflective Intelligence Layer for AI Systems; local-first reflective intelligence layer for AI systems; The portal is only the doorway; observable, diagnosable, bounded; v0.8.1 UI cleanup line; GitHub / README / Docs; Failure Modes / Doctor Gateway; Gates are certificates.; Only heal the active wound.; v0.9.3 AI Loop Toolkit Expansion; v0.9.4 Personal Coding Paradise; AI Toolbelt Console; Toolbelt Cockpit Output; toolbelt-json; Before any future generated script changes this repo, read `chatgpt/scripts.md`.
## Operator Surface Map
| Surface | Status |
|---|---|
| Spiral Core Desktop Portal | current blue/light-blue Spiral Core Portal |
| Neural Activity | Canonical visual organ |
| GitHub / README / Docs | resource submenu |
| Failure Modes / Doctor Gateway | diagnosis surface |
## Documentation Map
| Need | File |
|---|---|
| Balanced chat layout | `docs/runtime/NEXUS_UI_BALANCED_CHAT_LAYOUT.md` |
| Neural Activity | `docs/runtime/NEXUS_NEURAL_ACTIVITY.md` |
| Spiral Core Portal | `docs/runtime/NEXUS_SPIRAL_CORE_PORTAL.md` |
| AI Toolbelt | `docs/runtime/NEXUS_AI_TOOLBELT.md` |
| Toolbelt Cockpit | `docs/runtime/NEXUS_TOOLBELT_COCKPIT.md` |
| ChatGPT scripting doctrine | `chatgpt/scripts.md` |
<!-- NEXUS:README_023N_FRESHNESS_END -->

## AI Toolbelt / Nexus Loops
AI Toolbelt Console, Toolbelt Cockpit Output, and NEXUS Loop Cards are exposed through `toolbelt-start`, `toolbelt-dashboard`, `toolbelt-json`, `state/loops/nexus_loop_cards_latest.json`, and `docs/runtime/NEXUS_LOOP_CARDS.md`.
## What this is not
Not production validated. Not a safety proof. Not a security proof. Not a correctness proof. Not autonomous authority. Not write authority. Not memory write authority. Not provider authority. Not a replacement for human authorization. Not a claim that routing proves alignment. Not a claim that RHP proves truth. Not a claim that Nexus geometry proves code correctness. Not a claim that NexusCell is a perfect sandbox or full rollback proof.
## Compact Law
```text
Reflective intelligence is permitted. Autonomous authority is not. Organic evolution is allowed. Ungated compounding is not. Gates are certificates; active wounds resume without backtracking; evidence files are truth; stdout tails are smoke only.
```
Operator commands: `.\scripts\nexus.ps1 phi-loop-auto -Tag "microdose"`; `.\scripts\nexus.ps1 phi-gate-auto -Gate ci-core -Tag "supervise"`.
