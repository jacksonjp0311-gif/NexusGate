# NEXUS GATE

**Governed Agentic Transfer Layer for Modular AI Frameworks**

NEXUS GATE is a local-first software architecture and development runtime for bridging agent frameworks through governed state transfer, schema contracts, codec transforms, authority gates, shadow execution, replay certification, wound routing, demotion, recalibration, and clean disengagement.

It is not another agent framework. It is the transfer boundary between frameworks.

```text
Agent Framework
  -> FrameworkAdapter
  -> StatePacket
  -> NEXUS GATE Hot Route Plane
  -> reject | abstain | shadow | engage | defer | escalate
  -> Cold Evidence Plane
  -> replay | wound | demotion | recalibration | retirement
  -> ledger | report | registry update
```

## Core Claim

NEXUS GATE moves **permissioned operational meaning**, not just raw data.

A normal integration passes payloads. NEXUS GATE asks:

```text
What is the packet?
Where did it come from?
Which adapter normalized it?
Which schema governs it?
Which action is requested?
Which authority is allowed?
Which authority is denied?
Can this run live?
Must this run in shadow?
Can the result write memory?
Did this specialist fail before?
Was it wounded?
Was it recalibrated?
Can it disengage cleanly?
```

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
```

## Dual-Shell Development Rules

```text
Every new runtime loop must exist in both PowerShell and Bash.
Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.
Every promotion path must call the gated compiler first.
Every shell surface must preserve the same gate semantics.
PowerShell and Bash are peer surfaces, not separate products.
```

These rules are enforced by the gated compiler.

## Current Status

NEXUS GATE is currently a local scaffold with a gated development compiler, a professional README, and a dual-shell runtime loop.

| Layer | Status |
|---|---|
| Repo scaffold | Installed |
| Python package shell | Installed |
| StatePacket contract | Installed |
| FrameworkAdapter base contract | Installed |
| Hot route plane | Minimal implementation |
| Gated compiler | Installed |
| PowerShell runtime surface | Installed |
| Bash runtime surface | Installed |
| Cross-shell compiler checks | Installed |
| Cold evidence engine | Planned |
| Replay engine | Planned |
| Wound routing engine | Planned |
| Demotion/recalibration engine | Planned |
| Real framework adapters | Planned |

## What This Is

- A governed bridge architecture for agent framework interoperability.
- A local-first development scaffold.
- A gated compiler for repo-state validation.
- A dual-shell runtime loop for repeated compile/test/report cycles.
- A foundation for adapters, replay, wounds, demotion, recalibration, and clean disengagement.

## What This Is Not

- Not production validated.
- Not a safety proof.
- Not a security proof.
- Not a correctness proof.
- Not autonomous authority.
- Not write authority.
- Not memory write authority.
- Not provider authority.
- Not a replacement for human authorization.
- Not a claim of AGI or consciousness.

## Repository Layout

```text
nexus-gate/
  nexus_gate/
    core/             # StatePacket and core contracts
    adapters/         # FrameworkAdapter contracts
    runtime/          # Hot route plane
    compiler/         # Gated development compiler
    evidence/         # Ledger and future cold evidence modules
    policies/         # Authority and routing policies
    schemas/          # Packaged schema copies

  docs/
    architecture/     # System architecture
    runtime/          # Compiler and loop docs
    authority/        # Authority boundary docs
    evidence/         # Evidence discipline docs
    adapters/         # Adapter contract docs
    release/          # Release/promotion gate docs

  schemas/            # JSON schemas
  registry/           # Manifest and registry records
  state/              # Current system state
  ledger/             # Append-only JSONL ledger
  reports/            # Compiler reports
  logs/               # Loop logs
  scripts/            # PowerShell and Bash runtime commands
  tests/              # Unit tests
```

## Quick Start — PowerShell

Run the gated compiler once:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate"
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

Run the dev loop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 5 -IntervalSeconds 5
```

Run continuous watch mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_watch.ps1
```

Show status:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_status.ps1
```

Run promotion gate:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_promote.ps1
```

## Quick Start — Bash / Git Bash / WSL / Linux / macOS

Run the gated compiler once:

```bash
cd ~/OneDrive/Desktop/nexus-gate
bash scripts/nexus_once.sh
```

Run the dev loop:

```bash
bash scripts/nexus_dev_loop.sh --max-cycles 5 --interval 5
```

Run continuous watch mode:

```bash
bash scripts/nexus_watch.sh
```

Show status:

```bash
bash scripts/nexus_status.sh
```

Run promotion gate:

```bash
bash scripts/nexus_promote.sh
```

## Gated Compiler

The compiler is not a machine-code compiler. It is a **development gate**.

```text
repository state
  -> required paths
  -> runtime laws
  -> README rules
  -> JSON parse
  -> forbidden bypass scan
  -> dual-shell surface check
  -> loop compiler-call check
  -> Python compile
  -> route contracts
  -> unit tests
  -> ledger append
  -> report
  -> pass | fail
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_compile.ps1
```

Bash:

```bash
bash scripts/nexus_compile.sh
```

Reports are written to:

```text
reports/nexus_compile_report_latest.json
reports/nexus_compile_report_YYYYMMDD_HHMMSS.json
```

## Gated Runtime Loop

The runtime loop repeatedly runs the compiler and records outcomes.

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_dev_loop.ps1 -MaxCycles 3
```

Bash:

```bash
bash scripts/nexus_dev_loop.sh --max-cycles 3
```

The loop never promotes failed builds.

## Development Rule

All new functionality should enter through this sequence:

```text
1. Add or update contract.
2. Add or update schema.
3. Add or update test.
4. Add PowerShell and Bash surfaces if it touches runtime loops.
5. Run compiler.
6. Inspect report.
7. Commit only after pass.
8. Promote only through promotion gate.
```

## Roadmap

### v0.1.3 — Cold Evidence Engine

- ShadowReport
- RetrospectiveSynergyReport
- ShadowFailure
- ShadowWound
- WoundRoute
- Evidence spool processing

### v0.1.4 — Replay and Demotion

- ReplayCertificate
- DemotionDecision
- RecalibrationPlan
- RetirementDecision
- Maturity ledger updates

### v0.1.5 — Framework Adapters

- OpenAI Agents adapter
- LangChain/LangGraph adapter
- CrewAI adapter
- AutoGen adapter
- Semantic Kernel adapter
- MCP adapter

### v0.2.0 — Runtime Bridge

- Adapter registry
- Tool receptor registry
- Hot/cold queue split
- Bounded live routing
- Evidence-gated promotion

## License

TBD.

## Author

James Paul Jackson

NEXUS GATE is part of the Codex lineage of governed software architecture experiments.