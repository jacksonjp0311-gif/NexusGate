# NEXUS Personal Coding Paradise

v0.9.4 turns the AI loop toolkit into a personal coding paradise: a local, read-only, JSON-producing cockpit for creative planning, debug recovery, documentation weaving, safe shipping, and continuity.

The AI may recommend loops. NexusGate runs loops locally. Packets become evidence. The compiler seals. The human authorizes durable mutation.

## Paradise Loops

### idea-forge

- Group: `Creative`
- Function: Generate bounded next-build ideas from repo state, loop cards, and current intent.
- Operator use: Use when the system is clean enough to evolve.
- Command: `python -m nexus_gate.loops.runner --root . --loop idea-forge --intent "<intent>" --execute --human-authorized --json`

### architecture-sketch

- Group: `Design`
- Function: Sketch the local architecture surfaces touched by a proposed feature.
- Operator use: Use before patching a new organ or loop family.
- Command: `python -m nexus_gate.loops.runner --root . --loop architecture-sketch --intent "<intent>" --execute --human-authorized --json`

### patch-plan

- Group: `Build Planning`
- Function: Convert intent into a minimal intended-file patch plan with gates.
- Operator use: Use before generating a closer script.
- Command: `python -m nexus_gate.loops.runner --root . --loop patch-plan --intent "<intent>" --execute --human-authorized --json`

### test-strategy

- Group: `Validation`
- Function: Select targeted tests, bounded suite policy, and compiler gates for a change.
- Operator use: Use before or after patching.
- Command: `python -m nexus_gate.loops.runner --root . --loop test-strategy --intent "<intent>" --execute --human-authorized --json`

### debug-lens

- Group: `Debug`
- Function: Summarize latest failure evidence into a single active wound lens.
- Operator use: Use after a failed gate.
- Command: `python -m nexus_gate.loops.runner --root . --loop debug-lens --intent "<intent>" --execute --human-authorized --json`

### refactor-map

- Group: `Design`
- Function: Map refactor candidates without changing files.
- Operator use: Use when code shape is getting dense.
- Command: `python -m nexus_gate.loops.runner --root . --loop refactor-map --intent "<intent>" --execute --human-authorized --json`

### ui-polish

- Group: `HUD`
- Function: Inspect HUD/operator surfaces and suggest visual/usability polishing moves.
- Operator use: Use before UI/HUD work.
- Command: `python -m nexus_gate.loops.runner --root . --loop ui-polish --intent "<intent>" --execute --human-authorized --json`

### performance-scout

- Group: `Performance`
- Function: Find lightweight performance and size signals without profiling side effects.
- Operator use: Use before optimizing or when tests feel slow.
- Command: `python -m nexus_gate.loops.runner --root . --loop performance-scout --intent "<intent>" --execute --human-authorized --json`

### docs-weaver

- Group: `Documentation`
- Function: Find docs that should be updated together to preserve orientation.
- Operator use: Use when changing any public-facing surface.
- Command: `python -m nexus_gate.loops.runner --root . --loop docs-weaver --intent "<intent>" --execute --human-authorized --json`

### memory-anchor

- Group: `Continuity`
- Function: Build a compact continuity anchor with HEAD, latest commits, current loops, and doctrine.
- Operator use: Use before handoff or session restart.
- Command: `python -m nexus_gate.loops.runner --root . --loop memory-anchor --intent "<intent>" --execute --human-authorized --json`

### command-palette

- Group: `Operator Tools`
- Function: Emit all local loop command surfaces as a command palette.
- Operator use: Use when choosing what the AI should call next.
- Command: `python -m nexus_gate.loops.runner --root . --loop command-palette --intent "<intent>" --execute --human-authorized --json`

### session-brief

- Group: `Continuity`
- Function: Create a compact session brief for ChatGPT/Codex continuation.
- Operator use: Use at the end or start of a work block.
- Command: `python -m nexus_gate.loops.runner --root . --loop session-brief --intent "<intent>" --execute --human-authorized --json`

### commit-story

- Group: `Release`
- Function: Draft the human release story from intended changes and loop evidence.
- Operator use: Use before commit messages or release summaries.
- Command: `python -m nexus_gate.loops.runner --root . --loop commit-story --intent "<intent>" --execute --human-authorized --json`

### risk-register

- Group: `Safety`
- Function: List repo-local risks, dirty surfaces, boundary risks, and stale surfaces.
- Operator use: Use before staging or release-seal.
- Command: `python -m nexus_gate.loops.runner --root . --loop risk-register --intent "<intent>" --execute --human-authorized --json`

### paradise-index

- Group: `Coding Paradise`
- Function: Index all paradise loops as a personal coding cockpit.
- Operator use: Use when navigating the toolkit.
- Command: `python -m nexus_gate.loops.runner --root . --loop paradise-index --intent "<intent>" --execute --human-authorized --json`

### code-garden-map

- Group: `Design`
- Function: Map code/docs/tests/electron surfaces as a garden of organs.
- Operator use: Use for orientation before large changes.
- Command: `python -m nexus_gate.loops.runner --root . --loop code-garden-map --intent "<intent>" --execute --human-authorized --json`

### friction-detector

- Group: `Debug`
- Function: Detect workflow friction such as dirty tree, stale versions, backups, and failed compiler gates.
- Operator use: Use when progress feels stuck.
- Command: `python -m nexus_gate.loops.runner --root . --loop friction-detector --intent "<intent>" --execute --human-authorized --json`

### local-oracle

- Group: `Orchestration`
- Function: Recommend the next three loops from current local evidence.
- Operator use: Use when asking what should happen next.
- Command: `python -m nexus_gate.loops.runner --root . --loop local-oracle --intent "<intent>" --execute --human-authorized --json`

### pair-programming-brief

- Group: `Continuity`
- Function: Emit a brief that tells ChatGPT exactly how to help next.
- Operator use: Use before asking the AI for a closer or analysis.
- Command: `python -m nexus_gate.loops.runner --root . --loop pair-programming-brief --intent "<intent>" --execute --human-authorized --json`

### continuity-seal

- Group: `Continuity`
- Function: Verify that docs, loop cards, registry, resume packet, and compiler evidence are visible.
- Operator use: Use before ending a session.
- Command: `python -m nexus_gate.loops.runner --root . --loop continuity-seal --intent "<intent>" --execute --human-authorized --json`

## Composite Chains

### paradise-preflight

- Function: Combines awareness, environment, authority boundary, and available loop commands before a build session.
- Operator use: Use at the beginning of a serious coding session.

### creative-build-chain

- Function: Turns creative intent into a bounded, testable build plan.
- Operator use: Use when designing a new feature or tool loop.

### debug-recovery-chain

- Function: Resumes from wounds without rerunning green gates.
- Operator use: Use immediately after a failed gate or compiler failure.

### safe-ship-chain

- Function: Prepares a clean release narrative without granting commit or push authority.
- Operator use: Use before release-seal and human-authorized commit/push.

## Boundary

These loops do not grant autonomous authority, arbitrary command execution, network access, secret access, git write authority, safety proof, security proof, correctness proof, or production readiness.
