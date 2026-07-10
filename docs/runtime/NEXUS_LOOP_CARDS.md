# NEXUS Loop Cards

NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.
v0.9.7 includes Toolbelt Cockpit and Toolbelt JSON Packet cards.

Boundary: cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.

## Card Surfaces

- `state/loops/nexus_loop_cards.v0.9.7.json`
- `state/loops/nexus_loop_cards_latest.json`
- `python -m nexus_gate.loops.cards --root . --json`

## Cards

### Ai Orchestrator Preflight

- Loop: `ai-orchestrator-preflight`
- Group: `Meta Loops`
- Function: Prepare AI meta-orchestration context before choosing the next local loop.
- Command: `python -m nexus_gate.loops.runner --root . --loop ai-orchestrator-preflight --intent "<intent>" --json`

### Alignment Score

- Loop: `alignment-score`
- Group: `Alignment`
- Function: Produces a lightweight score explaining what is aligned, weak, missing, or dirty.
- Command: `python -m nexus_gate.loops.runner --root . --loop alignment-score --intent "<intent>" --json`

### Architecture Sketch

- Loop: `architecture-sketch`
- Group: `Design`
- Function: Sketch the local architecture surfaces touched by a proposed feature.
- Command: `python -m nexus_gate.loops.runner --root . --loop architecture-sketch --intent "<intent>" --json`

### Boundary Scan

- Loop: `boundary-scan`
- Group: `Safety`
- Function: Checks that new tools remain local, non-autonomous, non-network, non-secret, and non-git-write by default.
- Command: `python -m nexus_gate.loops.runner --root . --loop boundary-scan --intent "<intent>" --json`

### Bounded Validation

- Loop: `bounded-validation`
- Group: `Meta Loops`
- Function: Run compileall, bounded tests, and compiler.
- Command: `python -m nexus_gate.loops.runner --root . --loop bounded-validation --intent "<intent>" --json`

### Claim Boundary Audit

- Loop: `claim-boundary-audit`
- Group: `Safety`
- Function: Keeps public claims aligned with NexusGate's non-authority and non-proof boundary.
- Command: `python -m nexus_gate.loops.runner --root . --loop claim-boundary-audit --intent "<intent>" --json`

### Code Garden Map

- Loop: `code-garden-map`
- Group: `Design`
- Function: Map code/docs/tests/electron surfaces as a garden of organs.
- Command: `python -m nexus_gate.loops.runner --root . --loop code-garden-map --intent "<intent>" --json`

### Command Palette

- Loop: `command-palette`
- Group: `Operator Tools`
- Function: Emit all local loop command surfaces as a command palette.
- Command: `python -m nexus_gate.loops.runner --root . --loop command-palette --intent "<intent>" --json`

### Commit Story

- Loop: `commit-story`
- Group: `Release`
- Function: Draft the human release story from intended changes and loop evidence.
- Command: `python -m nexus_gate.loops.runner --root . --loop commit-story --intent "<intent>" --json`

### Compiler Wound Focus

- Loop: `compiler-wound-focus`
- Group: `Meta Loops`
- Function: Run compiler and focus exact failed gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop compiler-wound-focus --intent "<intent>" --json`

### Continuity Seal

- Loop: `continuity-seal`
- Group: `Continuity`
- Function: Verify that docs, loop cards, registry, resume packet, and compiler evidence are visible.
- Command: `python -m nexus_gate.loops.runner --root . --loop continuity-seal --intent "<intent>" --json`

### Creative Build Chain

- Loop: `creative-build-chain`
- Group: `Coding Paradise`
- Function: Turns creative intent into a bounded, testable build plan.
- Command: `python -m nexus_gate.loops.runner --root . --loop creative-build-chain --intent "<intent>" --json`

### Debug Lens

- Loop: `debug-lens`
- Group: `Debug`
- Function: Summarize latest failure evidence into a single active wound lens.
- Command: `python -m nexus_gate.loops.runner --root . --loop debug-lens --intent "<intent>" --json`

### Debug Recovery Chain

- Loop: `debug-recovery-chain`
- Group: `Coding Paradise`
- Function: Resumes from wounds without rerunning green gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop debug-recovery-chain --intent "<intent>" --json`

### Dependency Preflight

- Loop: `dependency-preflight`
- Group: `Environment`
- Function: Separates code wounds from environment wounds before patching.
- Command: `python -m nexus_gate.loops.runner --root . --loop dependency-preflight --intent "<intent>" --json`

### Docs Doctrine Preflight

- Loop: `docs-doctrine-preflight`
- Group: `Meta Loops`
- Function: Read README, doctrine, loop fabric, and cards docs before coding.
- Command: `python -m nexus_gate.loops.runner --root . --loop docs-doctrine-preflight --intent "<intent>" --json`

### Docs Weaver

- Loop: `docs-weaver`
- Group: `Documentation`
- Function: Find docs that should be updated together to preserve orientation.
- Command: `python -m nexus_gate.loops.runner --root . --loop docs-weaver --intent "<intent>" --json`

### Evolution Radar

- Loop: `evolution-radar`
- Group: `Evolution`
- Function: Keeps the system evolving by ranking next useful loops, HUD surfaces, tests, and compiler gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop evolution-radar --intent "<intent>" --json`

### Failure Intelligence

- Loop: `failure-intelligence`
- Group: `Meta Loops`
- Function: Read latest wound and failure surfaces so the next patch closes the exact wound instead of drifting.
- Command: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --json`

### Friction Detector

- Loop: `friction-detector`
- Group: `Debug`
- Function: Detect workflow friction such as dirty tree, stale versions, backups, and failed compiler gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop friction-detector --intent "<intent>" --json`

### Handoff Pack

- Loop: `handoff-pack`
- Group: `Continuity`
- Function: Creates a portable context packet with HEAD, changed surfaces, loops, cards, wounds, and recommended next action.
- Command: `python -m nexus_gate.loops.runner --root . --loop handoff-pack --intent "<intent>" --json`

### Hud Loop Sync

- Loop: `hud-loop-sync`
- Group: `Meta Loops`
- Function: Regenerate HUD-ready loop cards.
- Command: `python -m nexus_gate.loops.runner --root . --loop hud-loop-sync --intent "<intent>" --json`

### Idea Forge

- Loop: `idea-forge`
- Group: `Creative`
- Function: Generate bounded next-build ideas from repo state, loop cards, and current intent.
- Command: `python -m nexus_gate.loops.runner --root . --loop idea-forge --intent "<intent>" --json`

### Impact Map

- Loop: `impact-map`
- Group: `Meta Loops`
- Function: Build read-only GITNEXUS impact evidence.
- Command: `python -m nexus_gate.loops.runner --root . --loop impact-map --intent "<intent>" --json`

### Local Oracle

- Loop: `local-oracle`
- Group: `Orchestration`
- Function: Recommend the next three loops from current local evidence.
- Command: `python -m nexus_gate.loops.runner --root . --loop local-oracle --intent "<intent>" --json`

### Memory Anchor

- Loop: `memory-anchor`
- Group: `Continuity`
- Function: Build a compact continuity anchor with HEAD, latest commits, current loops, and doctrine.
- Command: `python -m nexus_gate.loops.runner --root . --loop memory-anchor --intent "<intent>" --json`

### Next Action Router

- Loop: `next-action-router`
- Group: `Orchestration`
- Function: Turns local evidence into an AI-orchestratable next-loop recommendation.
- Command: `python -m nexus_gate.loops.runner --root . --loop next-action-router --intent "<intent>" --json`

### Pair Programming Brief

- Loop: `pair-programming-brief`
- Group: `Continuity`
- Function: Emit a brief that tells ChatGPT exactly how to help next.
- Command: `python -m nexus_gate.loops.runner --root . --loop pair-programming-brief --intent "<intent>" --json`

### Paradise Index

- Loop: `paradise-index`
- Group: `Coding Paradise`
- Function: Index all paradise loops as a personal coding cockpit.
- Command: `python -m nexus_gate.loops.runner --root . --loop paradise-index --intent "<intent>" --json`

### Paradise Preflight

- Loop: `paradise-preflight`
- Group: `Coding Paradise`
- Function: Combines awareness, environment, authority boundary, and available loop commands before a build session.
- Command: `python -m nexus_gate.loops.runner --root . --loop paradise-preflight --intent "<intent>" --json`

### Patch Plan

- Loop: `patch-plan`
- Group: `Build Planning`
- Function: Convert intent into a minimal intended-file patch plan with gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop patch-plan --intent "<intent>" --json`

### Performance Scout

- Loop: `performance-scout`
- Group: `Performance`
- Function: Find lightweight performance and size signals without profiling side effects.
- Command: `python -m nexus_gate.loops.runner --root . --loop performance-scout --intent "<intent>" --json`

### Phi Gate Auto Repair

- Loop: `phi-gate-auto`
- Group: `Phi Microdose`
- Function: Bounded recovery autonomy for known deterministic wounds only; no arbitrary patching or git authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-gate-auto --intent "<intent>" --json`

### Phi Gate Supervisor

- Loop: `phi-gate-supervisor`
- Group: `Phi Microdose`
- Function: Failure-boundary microdose: pass continues; fail compresses, calls Phi, selects allowlisted repair, and reruns only when authorized.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-gate-supervisor --intent "<intent>" --json`

### Phi Loop Auto

- Loop: `phi-loop-auto`
- Group: `AI Microdose`
- Function: Bounded loop steering with local Phi; no mutation authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-loop-auto --intent "<intent>" --json`

### Phi Microdose Loop

- Loop: `phi-microdose-loop`
- Group: `AI Microdose`
- Function: Small local AI reasoning dose over file-backed Nexus evidence.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-microdose-loop --intent "<intent>" --json`

### Phi Wound Advisor

- Loop: `phi-wound-advisor`
- Group: `Wound Intelligence`
- Function: Ask local Phi-4 Mini to diagnose the active wound without giving it repo, shell, git, network, or secret authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-wound-advisor --intent "<intent>" --json`

### Phi Wound GPU Gate

- Loop: `phi-wound-gpu-gate`
- Group: `Wound Intelligence`
- Function: Separate model gate for local Phi-4 Mini base model advisory analysis.
- Command: `python -m nexus_gate.loops.runner --root . --loop phi-wound-gpu-gate --intent "<intent>" --json`

### Preflight Optimizer

- Loop: `preflight-optimizer`
- Group: `Operator Tools`
- Function: Check command parity, packet contracts, README freshness, bounded report shape, and ignored staging risk before mutation.
- Command: `python -m nexus_gate.loops.runner --root . --loop preflight-optimizer --intent "<intent>" --json`

### Refactor Map

- Loop: `refactor-map`
- Group: `Design`
- Function: Map refactor candidates without changing files.
- Command: `python -m nexus_gate.loops.runner --root . --loop refactor-map --intent "<intent>" --json`

### Reflective Validation

- Loop: `reflective-validation`
- Group: `Meta Loops`
- Function: Run compiler/test gates and convert failure into compact local intelligence.
- Command: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --json`

### Release Brief

- Loop: `release-brief`
- Group: `Promotion`
- Function: Gives the human a compact release summary before commit/push.
- Command: `python -m nexus_gate.loops.runner --root . --loop release-brief --intent "<intent>" --json`

### Release Seal

- Loop: `release-seal`
- Group: `Meta Loops`
- Function: Final local evidence before human-authorized commit/push.
- Command: `python -m nexus_gate.loops.runner --root . --loop release-seal --intent "<intent>" --json`

### Repo Radar

- Loop: `repo-radar`
- Group: `Awareness`
- Function: Summarize HEAD, dirty state, loop/card counts, compiler status, and next visibility surfaces.
- Command: `python -m nexus_gate.loops.runner --root . --loop repo-radar --intent "<intent>" --json`

### Rhp Core

- Loop: `rhp-core`
- Group: `Meta Loops`
- Function: Deep repository-origin rehydration before patching or compounding.
- Command: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --json`

### Risk Register

- Loop: `risk-register`
- Group: `Safety`
- Function: List repo-local risks, dirty surfaces, boundary risks, and stale surfaces.
- Command: `python -m nexus_gate.loops.runner --root . --loop risk-register --intent "<intent>" --json`

### Safe Ship Chain

- Loop: `safe-ship-chain`
- Group: `Coding Paradise`
- Function: Prepares a clean release narrative without granting commit or push authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop safe-ship-chain --intent "<intent>" --json`

### Scope Hygiene

- Loop: `scope-hygiene`
- Group: `Safety`
- Function: Prevents accidental staging by producing a scope-hygiene packet before commit or cleanup.
- Command: `python -m nexus_gate.loops.runner --root . --loop scope-hygiene --intent "<intent>" --json`

### Script Evolution

- Loop: `script-evolution`
- Group: `Meta Loops`
- Function: Plan and bound a generated script so the script triggers local intelligence instead of duplicating it.
- Command: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --json`

### Session Brief

- Loop: `session-brief`
- Group: `Continuity`
- Function: Create a compact session brief for ChatGPT/Codex continuation.
- Command: `python -m nexus_gate.loops.runner --root . --loop session-brief --intent "<intent>" --json`

### Stale Surface Scan

- Loop: `stale-surface-scan`
- Group: `Maintenance`
- Function: Highlights places where docs or tests may still point at old current-state claims.
- Command: `python -m nexus_gate.loops.runner --root . --loop stale-surface-scan --intent "<intent>" --json`

### Surface Map

- Loop: `surface-map`
- Group: `Architecture`
- Function: Gives the AI a repo topology map so future patches can target the correct organ.
- Command: `python -m nexus_gate.loops.runner --root . --loop surface-map --intent "<intent>" --json`

### System Monitor Scout

- Loop: `system-monitor-scout`
- Group: `Performance`
- Function: Route system monitor evolution through a named read-only loop before UI or telemetry patches.
- Command: `python -m nexus_gate.loops.runner --root . --loop system-monitor-scout --intent "<intent>" --json`

### Test Strategy

- Loop: `test-strategy`
- Group: `Validation`
- Function: Select targeted tests, bounded suite policy, and compiler gates for a change.
- Command: `python -m nexus_gate.loops.runner --root . --loop test-strategy --intent "<intent>" --json`

### Toolbelt Cockpit

- Loop: `toolbelt-cockpit`
- Group: `Operator Tools`
- Function: Turns the Toolbelt packet into a human cockpit without granting authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-cockpit --intent "<intent>" --json`

### Toolbelt Console

- Loop: `toolbelt-console`
- Group: `Operator Tools`
- Function: Emit the Toolbelt Console dashboard packet.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-console --intent "<intent>" --json`

### Toolbelt Dashboard

- Loop: `toolbelt-dashboard`
- Group: `AI Toolbelt`
- Function: A single JSON dashboard for the AI and human to align on what tools exist and what should run next.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-dashboard --intent "<intent>" --json`

### Toolbelt Index

- Loop: `toolbelt-index`
- Group: `AI Toolbelt`
- Function: Creates the local command/toolbelt map for orientation, planning, debugging, documentation, shipping, and continuity.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-index --intent "<intent>" --json`

### Toolbelt JSON Packet

- Loop: `toolbelt-json`
- Group: `Operator Tools`
- Function: Provides file-backed JSON evidence for the Toolbelt cockpit and recommended next loop.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-json --intent "<intent>" --json`

### Toolbelt Next

- Loop: `toolbelt-next`
- Group: `Meta Loops`
- Function: toolbelt_next
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-next --intent "<intent>" --json`

### Toolbelt Process

- Loop: `toolbelt-process`
- Group: `Meta Loops`
- Function: toolbelt_process
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-process --intent "<intent>" --json`

### Toolbelt Ship

- Loop: `toolbelt-ship`
- Group: `AI Toolbelt`
- Function: Chains hygiene, boundary, release brief, and release seal evidence before a human-authorized commit/push script.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-ship --intent "<intent>" --json`

### Toolbelt Ship Console

- Loop: `toolbelt-ship-console`
- Group: `Meta Loops`
- Function: toolbelt_ship
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-ship-console --intent "<intent>" --json`

### Toolbelt Start

- Loop: `toolbelt-start`
- Group: `AI Toolbelt`
- Function: Boots the personal coding paradise flow without giving the AI direct authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop toolbelt-start --intent "<intent>" --json`

### Ui Polish

- Loop: `ui-polish`
- Group: `HUD`
- Function: Inspect HUD/operator surfaces and suggest visual/usability polishing moves.
- Command: `python -m nexus_gate.loops.runner --root . --loop ui-polish --intent "<intent>" --json`

### Validate Promote

- Loop: `validate-promote`
- Group: `Meta Loops`
- Function: Verify candidate patch and stop before commit/push unless the human-authorized outer script performs it.
- Command: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --json`

### Wound Compression Engine

- Loop: `wound-compression-engine`
- Group: `Wound Intelligence`
- Function: Compress active wound evidence without granting mutation authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop wound-compression-engine --intent "<intent>" --json`

### Wound Indexed Resume

- Loop: `wound-indexed-resume`
- Group: `Meta Loops`
- Function: Emit active wound and resume recommendation.
- Command: `python -m nexus_gate.loops.runner --root . --loop wound-indexed-resume --intent "<intent>" --json`
