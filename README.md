# NEXUS GATE

**Governed Agentic Transfer Layer for Modular AI Frameworks**

NEXUS GATE is a local-first governed runtime for transferring permissioned operational meaning across agent frameworks. It routes agent state, tool intent, memory signals, framework events, and execution authority through explicit contracts, authority gates, RHP rehydration checks, shadow execution, evidence ledgers, failure-mode routing, and clean disengagement.

It is not another agent framework. It is the governed transfer boundary between frameworks.

```text
Human intent
  -> RHP origin alignment
  -> FrameworkAdapter
  -> StatePacket
  -> NEXUS GATE hot route plane
  -> reject | abstain | shadow | engage | defer | escalate
  -> cold evidence plane
  -> failure mode | wound | demotion | replay | recalibration
  -> ledger | report | registry update
```

## Repository Description

NEXUS GATE combines three layers:

1. **Human control layer**: a readable director box, quick-start commands, safety boundaries, current health, and operator rules.
2. **RHP Nexus layer**: repository origin alignment, route maps, Echo Location records, mini READMEs, validation surfaces, and context indexes.
3. **AI agent layer**: operating contract, patch route, file routing guide, failure modes, non-claim locks, and done criteria.

Boundary: this repository surface improves developer discipline, local validation, agent orientation, and release hygiene. It does not prove code correctness, security, safety, production readiness, AI understanding, agent alignment, model correctness, empirical truth, or autonomous authority.

## Human Director Box

### What is this?

NEXUS GATE is a governed agentic transfer workbench. It tests whether a local runtime can normalize framework events into StatePackets, route them through schema and authority gates, compile the repository state, preserve evidence, expose failure modes, and keep humans and AI agents oriented through RHP/Nexus documentation.

### What changed in v0.1.3?

This update adds the full RHP/Nexus documentation shell:

- PART I - Human README
- PART II - RHP Nexus README
- PART III - AI Agent README
- folder-level mini READMEs with Echo Location records
- `docs/context/` repository indexes
- `rcc/nexus/` route maps and agent handoff contracts
- explicit failure-mode registry and failure-mode docs
- portable compressed PowerShell installer
- dual PowerShell/Bash runtime scripts
- compiler gates that require the README/RHP/Nexus/AI surface

### Current health snapshot

| Surface | Current result |
|---|---:|
| Package / CLI | `nexus-gate` / `nexus` |
| Python import | `nexus_gate` |
| Current software layer | NG-SA v0.1.3 |
| Current runtime status | local scaffold + gated compiler |
| README structure | Human / RHP Nexus / AI trisection |
| RHP origin alignment | scaffolded |
| RCC/Nexus route map | scaffolded |
| Mini README coverage | required for key folders |
| Evidence emission | state, reports, logs, ledger |
| Dual shell surface | PowerShell + Bash |
| Compiler gate | required |
| Claim status | local development gate only |
| Production status | not production validated |
| Next build target | v0.1.4 cold evidence engine |

### What this is not

- Not production validated.
- Not a safety proof.
- Not a security proof.
- Not a correctness proof.
- Not autonomous authority.
- Not write authority.
- Not memory write authority.
- Not provider authority.
- Not a replacement for human authorization.
- Not a claim that routing proves alignment.
- Not a claim that RHP proves truth.
- Not a claim that Nexus geometry proves code correctness.

### Where do I start?

PowerShell:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate"
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_status.ps1
```

Bash / Git Bash / WSL / Linux / macOS:

```bash
cd ~/OneDrive/Desktop/nexus-gate
bash scripts/nexus_once.sh
bash scripts/nexus_status.sh
```

---

# PART I - Human README

## Current Identity

NEXUS GATE is a local Python reference runtime and repository governance shell for testing whether agent-framework events can be:

- normalized into `StatePacket` contracts,
- routed through schema and authority gates,
- blocked when authority is missing,
- shadowed before live engagement,
- recorded in evidence ledgers,
- compiled through a local development gate,
- described through a Human/RHP Nexus/AI README trisection,
- navigated through folder-level mini READMEs,
- preserved through RHP origin-alignment discipline.

The current repo is a governed scaffold, not a production bridge.

## Runtime Laws

```text
No adapter, no bridge.
No schema, no route.
No codec, no transfer.
No profile, no coverage.
No calibration, no warning authority.
No shadow, no live promotion.
No authority verification, no mutation.
No replay certificate, no memory promotion.
No wound route, no retrust.
No clean disengagement, no connection.
No ledger stub, no compounding.
No compile pass, no promotion.
No RHP alignment, no durable mutation.
No mini README, no blind patching.
```

## Quick Start

Run once:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

Run dev loop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 5 -IntervalSeconds 5
```

Run status:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_status.ps1
```

Run promotion gate:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_promote.ps1
```

## Project Structure Director

| Surface | What it does | Why it matters |
|---|---|---|
| `AGENTS.md` | Agent entry beacon and operating contract. | Prevents blind patching. |
| `README.md` | Human / RHP Nexus / AI trisection. | Makes the repo readable by humans and agents. |
| `README_90_SECONDS.md` | Short adoption compression. | Reduces onboarding friction. |
| `nexus_gate/core/` | StatePacket and core contracts. | Defines transfer packets. |
| `nexus_gate/runtime/` | Hot route plane. | Holds route decision behavior. |
| `nexus_gate/compiler/` | Gated development compiler. | Blocks promotion when repo state fails. |
| `nexus_gate/evidence/` | Ledger and future evidence modules. | Preserves run continuity. |
| `docs/context/` | Repository context, validation surface, Nexus index. | Main self-description surface. |
| `docs/failure_modes/` | Failure-mode taxonomy and handling rules. | Makes expected failures explicit. |
| `docs/runtime/` | Compiler, loop, release-gate docs. | Explains operational commands. |
| `docs/software_architecture/` | NG-SA architecture docs. | Keeps theory-to-software direction explicit. |
| `rcc/nexus/` | Route maps, Echo template, handoff contract. | Makes the repo agent-navigable. |
| `scripts/` | PowerShell and Bash command surfaces. | Makes local operation repeatable. |
| `tests/` | Implementation-health tests. | Catches local scaffold regressions. |
| `state/` | Current system state. | Machine-readable project status. |
| `ledger/` | Append-only JSONL continuity records. | Preserves event history. |
| `reports/` | Compiler and validation reports. | Evidence surface for gate results. |
| `logs/` | Runtime and dev-loop logs. | Operational trace. |

## Failure Modes

| Failure mode | Meaning | Required response |
|---|---|---|
| `schema_missing` | Packet lacks schema identity. | Reject. |
| `authority_unverified` | Requested action lacks authority. | Shadow or reject. |
| `origin_dehydrated` | Session state drifted from repo origin. | Rehydrate before mutation. |
| `compiler_failed` | Repo state failed gated compiler. | No commit or promotion. |
| `mini_readme_missing` | Target folder lacks local orientation. | Repair mini README before patching. |
| `ledger_unavailable` | Evidence cannot be appended. | Block compounding. |
| `direct_compiler_call_missing` | Runtime script does not call compiler directly. | Repair script. |
| `claim_boundary_missing` | Report lacks non-claim boundary. | Block public-facing claim. |
| `shadow_failure_unrouted` | Shadow failure has no wound/failure route. | Convert to failure-mode record. |
| `replay_missing` | Re-engagement lacks replay certificate. | Block re-engagement. |

## Evidence Artifacts

Runtime state artifacts are written under:

```text
state/
```

Compiler reports are written under:

```text
reports/
```

Runtime logs are written under:

```text
logs/
```

Ledgers are written under:

```text
ledger/
```

RHP/Nexus context files live under:

```text
docs/context/
rcc/nexus/
```

## Non-Claim Locks

NEXUS GATE is:

- not proof of correctness,
- not proof of safety,
- not proof of security,
- not proof of production readiness,
- not proof that an agent may self-authorize,
- not proof that RHP alignment equals truth,
- not proof that Nexus geometry equals code quality,
- not proof that passing tests proves real-world safety,
- not proof that framework interoperability is validated beyond the declared local gates.

---

# PART II - RHP Nexus README

## RHP Nexus Identity

RHP tells the agent what origin it must rehydrate from.

Nexus tells the agent where it is.

Validation tells the agent whether the local repo state passed the gate.

NEXUS GATE uses RHP/Nexus to prevent blind continuation, context drift, and ungrounded mutation.

## Repository Sphere

| Shell | Name | Meaning |
|---|---|---|
| `center` | Invariant Core | Purpose, runtime laws, non-claim locks, authority boundaries. |
| `inner` | Contracts | StatePacket, FrameworkAdapter, schemas, authority contracts. |
| `middle` | Processes | Compiler, scripts, tests, validation, dev loop. |
| `outer` | Evidence / Reflection | Ledgers, reports, logs, context indexes, release notes. |

## Nexus Meridians

- origin
- authority
- schema
- runtime
- compiler
- evidence
- failure
- agent
- release
- documentation

## Nexus Sectors

- core
- adapters
- runtime
- compiler
- evidence
- policies
- schemas
- scripts
- tests
- docs
- release

## Primary Nexus Files

- `docs/context/repository_context_index.json`
- `docs/context/rcc_nexus_index.json`
- `docs/context/validation_surface.md`
- `rcc/nexus/README.md`
- `rcc/nexus/route_map.json`
- `rcc/nexus/task_routing_matrix.md`
- `rcc/nexus/echo_location_template.md`
- `rcc/nexus/agent_handoff_contract.md`
- `docs/failure_modes/FAILURE_MODES.md`
- `reports/nexus_compile_report_latest.json`

## RHP Origin Alignment

A session is not allowed to treat memory, chat context, or prior guesses as authoritative when the repository exists locally.

Required sequence:

```text
Anchor repo
  -> read README
  -> read docs/context/repository_context_index.json
  -> read docs/context/rcc_nexus_index.json
  -> read rcc/nexus/route_map.json
  -> read target folder README
  -> inspect relevant source/tests/docs
  -> patch minimal surface
  -> run compiler
  -> update ledger/report/context if geometry changed
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): origin, authority, runtime, compiler, evidence
- Sector: rcc
- Version / TTL: NG-RHP-NEXUS-v0.1.3 / 180 days
- Last Verified: generated by installer

Local Role:

- Root orientation surface for humans, RHP Nexus routing, and AI agents.

Inbound Hooks:

- local PowerShell installer
- local Bash scripts
- Git repository
- NEXUS GATE compiler

Outbound Hooks:

- `docs/context/repository_context_index.json`
- `docs/context/rcc_nexus_index.json`
- `docs/context/validation_surface.md`
- `rcc/nexus/route_map.json`
- `nexus_gate/runtime/router.py`
- `nexus_gate/compiler/compiler.py`
- `tests/`
- `reports/`

Evidence Surface:

- `reports/`
- `state/`
- `logs/`
- `ledger/`

Validation Surface:

- `python -m compileall nexus_gate tests`
- `python -m unittest discover -s tests`
- `python -m nexus_gate.compiler --root . --json`
- `powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1`
- `bash scripts/nexus_once.sh`

Claim Boundary:

- README quality, RHP origin alignment, RCC/Nexus geometry, reports, and ledgers do not prove code correctness, security, patch safety, AI understanding, production readiness, or runtime truth.

Non-Claim Locks:

- rhp_alignment_is_not_truth
- nexus_geometry_is_not_correctness
- navigation_is_not_validation
- context_reconstruction_is_not_code_quality
- validation_remains_required
- compiler_pass_is_local_gate_only

Agent Route:

- Read `README.md`, `docs/context/repository_context_index.json`, `docs/context/rcc_nexus_index.json`, `rcc/nexus/route_map.json`, then the target folder README before editing.

Update Obligation:

- Update README, RHP context, Nexus index, route maps, validation surface, failure modes, reports, and Echo Location records when project identity, validation commands, evidence paths, claim boundaries, or repository geometry changes.

## RHP Nexus Non-Claim Lock

RHP/Nexus improves navigation, traceability, maintenance discipline, and agent self-location. It does not prove code correctness, security, AI understanding, patch safety, production readiness, causal mechanism, or runtime truth.

Geometry is not correctness.

Navigation is not validation.

Context is not truth.

---

# PART III - AI Agent README

## AI Version Tracking Contract

Current repository context:

- Repository: nexus-gate
- Purpose: governed agentic transfer layer and local development gate.
- Current runtime layer: NEXUS GATE scaffold.
- Current software architecture layer: NG-SA v0.1.3 RHP/Nexus/AI repo shell.
- Primary package: `nexus_gate`.
- CLI: `nexus`.
- Current classification: local development gate only.
- Current non-claim boundary: local scaffold evidence only, not production validation.
- RHP mode: origin alignment before durable mutation.
- Nexus mode: local geometric repository navigation shell plus mini READMEs.
- No runtime behavior is changed by documentation alone.

## AI Operating Contract

Any AI agent reading or modifying this repository must follow this order:

1. Read the Human Director Box.
2. Read PART I - Human README.
3. Read PART II - RHP Nexus README.
4. Read PART III - AI Agent README.
5. Read `docs/context/repository_context_index.json`.
6. Read `docs/context/rcc_nexus_index.json`.
7. Read `docs/context/validation_surface.md`.
8. Read `rcc/nexus/route_map.json`.
9. Read the mini README in the target folder.
10. Inspect only relevant source, tests, docs, configs, scripts, reports, outputs, or visuals.
11. Patch the smallest necessary surface.
12. Run the gated compiler before claiming behavior changed.
13. Update README, RHP, Nexus, reports, and Echo Location records if geometry or evidence changed.

## AI README Update Policy

When the repository versions, the AI agent must update the root README in all required zones.

Required root README update zones:

| Zone | Section | Required update |
|---|---|---|
| 1 | Human Director Box / Current health snapshot | Current software layer, latest patch, tests, release reference, gate status. |
| 2 | PART I - Human README | Project structure, quick start, failure modes, evidence paths. |
| 3 | PART II - RHP Nexus README | Repository sphere, route maps, context indexes, Echo Location. |
| 4 | PART III - AI Agent README | Version tracking, operating contract, done criteria. |
| 5 | Failure Modes | New failure modes and responses. |
| 6 | Directory / Mini README Coverage | New folders and local orientation blocks. |
| 7 | Validation commands | Update commands if validation surface changed. |
| 8 | Boundary / non-claim locks | Preserve or strengthen boundaries; never weaken them. |

AI update rule:

```text
Top dashboard without AI route is incomplete.
AI route without RHP/Nexus context is blind.
Current version without failure-mode update is drift.
README completion requires all three: human state, RHP/Nexus state, AI operating state.
```

## AI File Routing Guide

- `nexus_gate/core`: StatePacket and core transfer contracts.
- `nexus_gate/adapters`: framework adapter interfaces.
- `nexus_gate/runtime`: hot route plane and mode decisions.
- `nexus_gate/compiler`: gated development compiler.
- `nexus_gate/evidence`: ledger and future evidence modules.
- `nexus_gate/policies`: authority policy contracts.
- `nexus_gate/schemas`: packaged schemas.
- `docs/context`: repository context index, validation surface, Nexus index.
- `docs/failure_modes`: failure taxonomy and handling rules.
- `docs/software_architecture`: software architecture shell.
- `docs/runtime`: compiler, loop, release docs.
- `rcc/nexus`: route map, task matrix, Echo template, handoff contract.
- `scripts`: PowerShell and Bash runtime surfaces.
- `tests`: implementation-health validation.
- `state`: machine-readable system state.
- `ledger`: JSONL continuity records.
- `reports`: compiler and validation reports.
- `logs`: runtime logs.

## AI Non-Claim Lock

Never claim or imply:

- NEXUS GATE proves correctness.
- NEXUS GATE proves safety.
- NEXUS GATE proves production readiness.
- NEXUS GATE grants autonomous write authority.
- NEXUS GATE grants tool authority by itself.
- RHP alignment proves truth.
- Nexus navigation proves code quality.
- Passing local compiler gates proves real-world safety.
- Agent fluency should be confused with source-grounded implementation accuracy.

## Required Local Verification

After README, RHP, Nexus, or mini README changes, run:

```powershell
python -m nexus_gate.compiler --root . --json
python -m unittest discover -s tests
```

After source/runtime changes, also run:

```powershell
python -m compileall nexus_gate tests
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

## Done Criteria

A change is not complete until:

- runtime laws are preserved,
- RHP origin alignment is preserved,
- non-claim locks are preserved,
- target folder README remains accurate,
- context index remains accurate,
- route map remains accurate,
- compiler passed,
- tests passed,
- evidence paths are updated if outputs changed,
- claims remain inside evidence boundaries.


## Dual-Shell Development Rule

```text
Every new runtime loop must exist in both PowerShell and Bash.
Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.
Every promotion path must call the gated compiler first.
Every shell surface must preserve the same gate semantics.
PowerShell and Bash are peer surfaces, not separate products.
```

## Rehydration Failure and Update Visibility Rule

Every agent rehydration must expose the current failure-mode chart and update chart before patching.

```text
No rehydration without failure chart visibility.
No patch without update chart visibility.
No agent handoff without latest compiler report visibility.
No recovery without failure mode classification.
No version step without update ledger entry.
```

Required rehydration read order:

```text
1. README.md
2. docs/context/REHYDRATION_BOOT.md
3. docs/context/rehydration_manifest.v0.1.4.json
4. docs/failure_modes/FAILURE_MODE_CHART.md
5. docs/updates/UPDATE_CHART.md
6. state/failure_mode_index.v0.1.4.json
7. state/update_index.v0.1.4.json
8. reports/nexus_compile_report_latest.json, if present
9. rcc/nexus/route_map.json
10. target folder README.md
```

Agent rule:

```text
The agent must see failures, updates, reports, and route context during rehydration before it edits code.
```


## Compact Runtime Command Surface

NEXUS GATE now has a compact command surface.

PowerShell:

```powershell
.\scripts\nexus.ps1 rehydrate
.\scripts\nexus.ps1 compile
.\scripts\nexus.ps1 status
.\scripts\nexus.ps1 loop -Cycles 5
.\scripts\nexus.ps1 promote
```

Bash / Git Bash / WSL / Linux / macOS:

```bash
bash scripts/nexus.sh rehydrate
bash scripts/nexus.sh compile
bash scripts/nexus.sh status
bash scripts/nexus.sh loop --cycles 5
bash scripts/nexus.sh promote
```

Compact law:

```text
One command surface.
Same gates.
Less syntax.
No compile pass, no promotion.
No rehydration without failure/update visibility.
```

Windows rule:

```text
If Bash exists but WSL has no installed distribution, Bash validation is skipped locally.
Bash scripts still remain in the repo and CI can validate them on Ubuntu.
```


## v0.1.5 — Strict Compiler + Cold Evidence/Wound Routing

NEXUS GATE now begins the cold evidence layer.

New surfaces:

```text
ShadowReport
ShadowFailure
ShadowWound
WoundRoute
ReplayCertificate
DemotionDecision
ColdEvidenceEngine
```

New compile law:

```text
No shadow failure without wound route.
No re-engagement without replay certificate.
No specialist promotion without cold evidence.
No compiler pass without cold evidence contract visibility.
```

Strict compile:

```powershell
.\scripts\nexus_strict_compile.ps1
```

Compact strict route:

```powershell
.\scripts\nexus.ps1 compile
.\scripts\nexus.ps1 rehydrate
```


## v0.1.6 - Compression, Packing, and Goal Lock

NEXUS GATE is now past installer repair. The current goal is to keep the runtime compact, compiled, and aligned with the original architecture:

```text
Governed transfer boundary.
Adapter contracts.
Hot route plane.
Cold evidence plane.
Authority gates.
Wound routing.
Replay before retrust.
Clean disengagement.
```

New command:

```powershell
.\scripts\nexus.ps1 pack
```

This runs compile checks and writes a compressed repo bundle under:

```text
dist/
```

Compression law:

```text
No growing code surface without a pack report.
No release without compile, tests, compiler, and pack manifest.
No new feature unless it advances the governed transfer boundary.
```


## v0.1.7 - Adapter Registry + LocalDemoAdapter

NEXUS GATE now begins the actual bridge surface.

New adapter law:

```text
No adapter, no bridge.
No manifest, no registration.
No normalized StatePacket, no route.
No receptor export, no transfer target.
```

New compact commands:

```powershell
.\scripts\nexus.ps1 adapters
.\scripts\nexus.ps1 pack
```

New build lane:

```text
adapter registry -> adapter manifest -> LocalDemoAdapter -> StatePacket -> route decision
```

This version is still local development evidence only. It does not prove production interoperability.


## v0.1.8 - Receptor Registry + Compatibility Compiler

NEXUS GATE now has both sides of the first bridge lane:

```text
Adapter -> StatePacket -> Receptor -> CompatibilityDecision
```

New receptor law:

```text
No receptor, no transfer target.
No compatibility decision, no engagement.
No unsupported schema, no receptor route.
No unsupported action, no receptor route.
```

New compact command:

```powershell
.\scripts\nexus.ps1 receptors
```

This is still local development evidence only. It does not prove production interoperability.


## v0.1.9 - Bridge Session Runner

NEXUS GATE now has the first bounded local bridge session path:

```text
raw event
  -> LocalDemoAdapter
  -> StatePacket
  -> NexusRouter
  -> ReceptorManifest
  -> CompatibilityDecision
  -> BridgeSessionReport
```

New bridge law:

```text
No bridge session without adapter normalization.
No bridge session without route decision.
No bridge session without receptor compatibility.
No bridge report without claim boundary.
```

New compact command:

```powershell
.\scripts\nexus.ps1 bridge
```

This remains local development evidence only. It proves the local bridge session mechanics, not production interoperability.


## v0.2.0 - Bounded Bridge Runtime

NEXUS GATE now has the first bounded local bridge runtime.

Runtime flow:

```text
raw event batch
  -> BoundedBridgeRuntime
  -> BridgeSessionRunner per event
  -> BridgeSessionReport per event
  -> BoundedRuntimeReport
```

Runtime law:

```text
No runtime without event limit.
No runtime without bridge session reports.
No runtime without summary counts.
No runtime without claim boundary.
No promotion without runtime compiler pass.
```

New command:

```powershell
.\scripts\nexus.ps1 runtime
```

This is local development evidence only. It proves bounded runtime mechanics, not production interoperability.


## v0.2.1 - Human Surface + Quiet Git Warnings

NEXUS GATE now has a human-readable operator surface for PowerShell runs.

New command:

```powershell
.\scripts\nexus.ps1 human
```

Human surface law:

```text
No operator flood.
No raw JSON wall unless requested.
No CRLF warning noise in normal runs.
No completion claim without compiled report files.
```

The full evidence is still written under `reports/`. The terminal should show the human status path:

```text
compile
tests
NEXUS compiler
adapter compiler
receptor compiler
bridge compiler
runtime compiler
pack compiler
```

This is local development evidence only.


## v0.2.2 - Feedback + Interconnect + Evidence Compaction

NEXUS GATE now has an adaptive local feedback layer.

```powershell
.\scripts\nexus.ps1 compact
.\scripts\nexus.ps1 interconnect
.\scripts\nexus.ps1 feedback
.\scripts\nexus.ps1 evolve
```

The system now compiles:

```text
compiler reports
  -> evidence pressure
  -> interconnect graph
  -> feedback report
  -> next bounded action
```

New laws:

```text
No feedback without compiled reports.
No interconnect without governed edges.
No compaction without manifest.
No CLI evolution without human-readable surface.
No new runtime lane without feedback visibility.
```

Claim boundary: local development evidence only.


## v0.2.2b - Self-Healing Feedback Rescue

NEXUS GATE now has a CMS-inspired self-healing feedback lane:

```powershell
.\scripts\nexus.ps1 heal
.\scripts\nexus.ps1 evolve
```

The loop is:

```text
feedback finding
  -> typed repair recommendation
  -> dry-run repair plan
  -> human-authorized apply gate
  -> validation stack
  -> evidence report
```

Hard lock:

```text
No self-healing without typed recommendation.
No recommendation may write directly.
No dry-run may write target surfaces.
No apply gate may execute without explicit human authorization.
No repair closure without validation evidence.
No autonomous commit from self-healing recommendation.
```

This restores v0.2.2 compatibility markers and adds bounded self-healing reports without autonomous mutation.


## v0.2.3 - AI Feedback Interface + Markdown Feedback Log

NEXUS GATE now exposes its feedback loop as a first-class interface for future AI systems.

```powershell
.\scripts\nexus.ps1 interface
.\scripts\nexus.ps1 feedback
.\scripts\nexus.ps1 heal
.\scripts\nexus.ps1 evolve
```

Canonical AI read surfaces:

```text
state/ai_feedback_context_latest.json
docs/feedback/FEEDBACK_SYSTEM.md
docs/feedback/FEEDBACK_LOG.md
reports/nexus_feedback_interface_report_latest.json
```

The PowerShell human surface now prints a feedback summary after feedback/evolve runs:

```text
Health score
Evidence pressure
Dominant pressure
Next action
AI context path
Feedback log path
```

Two-way protocol:

```text
AI reads feedback context.
AI proposes typed recommendation.
AI does not assume autonomous write authority.
Human-authorized patch applies mutation.
Patch runs evolve.
Feedback interface appends FEEDBACK_LOG.md.
```
