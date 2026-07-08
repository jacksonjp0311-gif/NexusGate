# NEXUS Loop Cards

NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.
v0.9.3 expands cards into an AI Loop Toolkit: local evidence loops the AI can recommend while NexusGate preserves authority boundaries.

Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.

## Card Surfaces

- `state/loops/nexus_loop_cards.v0.9.3.json`
- `state/loops/nexus_loop_cards_latest.json`
- `python -m nexus_gate.loops.cards --root . --json`
- Spiral Core Portal option `[14] Nexus Loops / Cards`

## Cards

### Ai Orchestrator Preflight

- Loop: `ai-orchestrator-preflight`
- Group: `Meta Loops`
- Function: Prepare AI meta-orchestration context before choosing the next local loop.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop ai-orchestrator-preflight --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop ai-orchestrator-preflight --intent "<intent>" --execute --human-authorized --json`

### Alignment Score

- Loop: `alignment-score`
- Group: `Alignment`
- Function: Produces a lightweight score explaining what is aligned, weak, missing, or dirty.
- Operator use: Use after major changes to decide whether the system is ready for release-seal.
- Command: `python -m nexus_gate.loops.runner --root . --loop alignment-score --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop alignment-score --intent "<intent>" --execute --human-authorized --json`

### Boundary Scan

- Loop: `boundary-scan`
- Group: `Safety`
- Function: Checks that new tools remain local, non-autonomous, non-network, non-secret, and non-git-write by default.
- Operator use: Use before adding any new command or loop.
- Command: `python -m nexus_gate.loops.runner --root . --loop boundary-scan --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop boundary-scan --intent "<intent>" --execute --human-authorized --json`

### Bounded Validation

- Loop: `bounded-validation`
- Group: `Meta Loops`
- Function: Run compileall, bounded tests, and compiler.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop bounded-validation --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop bounded-validation --intent "<intent>" --execute --human-authorized --json`

### Claim Boundary Audit

- Loop: `claim-boundary-audit`
- Group: `Safety`
- Function: Keeps public claims aligned with NexusGate's non-authority and non-proof boundary.
- Operator use: Use before publishing README/docs or after large conceptual changes.
- Command: `python -m nexus_gate.loops.runner --root . --loop claim-boundary-audit --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop claim-boundary-audit --intent "<intent>" --execute --human-authorized --json`

### Compiler Wound Focus

- Loop: `compiler-wound-focus`
- Group: `Meta Loops`
- Function: Run compiler and focus exact failed gates.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop compiler-wound-focus --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop compiler-wound-focus --intent "<intent>" --execute --human-authorized --json`

### Dependency Preflight

- Loop: `dependency-preflight`
- Group: `Environment`
- Function: Separates code wounds from environment wounds before patching.
- Operator use: Use when a command fails unexpectedly or before UI/Electron work.
- Command: `python -m nexus_gate.loops.runner --root . --loop dependency-preflight --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop dependency-preflight --intent "<intent>" --execute --human-authorized --json`

### Docs Doctrine Preflight

- Loop: `docs-doctrine-preflight`
- Group: `Meta Loops`
- Function: Read README, doctrine, loop fabric, and cards docs before coding.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop docs-doctrine-preflight --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop docs-doctrine-preflight --intent "<intent>" --execute --human-authorized --json`

### Evolution Radar

- Loop: `evolution-radar`
- Group: `Evolution`
- Function: Keeps the system evolving by ranking next useful loops, HUD surfaces, tests, and compiler gates.
- Operator use: Use when asking what to build next without drifting away from alignment.
- Command: `python -m nexus_gate.loops.runner --root . --loop evolution-radar --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop evolution-radar --intent "<intent>" --execute --human-authorized --json`

### Failure Intelligence

- Loop: `failure-intelligence`
- Group: `Meta Loops`
- Function: Read latest wound and failure surfaces so the next patch closes the exact wound instead of drifting.
- Operator use: Use when this named loop matches the active gate or wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --execute --human-authorized --json`

### Handoff Pack

- Loop: `handoff-pack`
- Group: `Continuity`
- Function: Creates a portable context packet with HEAD, changed surfaces, loops, cards, wounds, and recommended next action.
- Operator use: Use before switching sessions, models, or tools.
- Command: `python -m nexus_gate.loops.runner --root . --loop handoff-pack --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop handoff-pack --intent "<intent>" --execute --human-authorized --json`

### Hud Loop Sync

- Loop: `hud-loop-sync`
- Group: `Meta Loops`
- Function: Regenerate HUD-ready loop cards.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop hud-loop-sync --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop hud-loop-sync --intent "<intent>" --execute --human-authorized --json`

### Impact Map

- Loop: `impact-map`
- Group: `Meta Loops`
- Function: Build read-only GITNEXUS impact evidence.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop impact-map --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop impact-map --intent "<intent>" --execute --human-authorized --json`

### Next Action Router

- Loop: `next-action-router`
- Group: `Orchestration`
- Function: Turns local evidence into an AI-orchestratable next-loop recommendation.
- Operator use: Use when the AI is unsure whether to rehydrate, clean scope, focus compiler, validate, or seal.
- Command: `python -m nexus_gate.loops.runner --root . --loop next-action-router --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop next-action-router --intent "<intent>" --execute --human-authorized --json`

### Reflective Validation

- Loop: `reflective-validation`
- Group: `Meta Loops`
- Function: Run compiler/test gates and convert failure into compact local intelligence.
- Operator use: Use when this named loop matches the active gate or wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --execute --human-authorized --json`

### Release Brief

- Loop: `release-brief`
- Group: `Promotion`
- Function: Gives the human a compact release summary before commit/push.
- Operator use: Use immediately before release-seal or after a compiler pass.
- Command: `python -m nexus_gate.loops.runner --root . --loop release-brief --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop release-brief --intent "<intent>" --execute --human-authorized --json`

### Release Seal

- Loop: `release-seal`
- Group: `Meta Loops`
- Function: Final local evidence before human-authorized commit/push.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop release-seal --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop release-seal --intent "<intent>" --execute --human-authorized --json`

### Repo Radar

- Loop: `repo-radar`
- Group: `Awareness`
- Function: Summarize HEAD, dirty state, loop/card counts, compiler status, and next visibility surfaces.
- Operator use: Use first when the AI needs situational awareness before selecting the next local loop.
- Command: `python -m nexus_gate.loops.runner --root . --loop repo-radar --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop repo-radar --intent "<intent>" --execute --human-authorized --json`

### Rhp Core

- Loop: `rhp-core`
- Group: `Meta Loops`
- Function: Deep repository-origin rehydration before patching or compounding.
- Operator use: Use when this named loop matches the active gate or wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --execute --human-authorized --json`

### Scope Hygiene

- Loop: `scope-hygiene`
- Group: `Safety`
- Function: Prevents accidental staging by producing a scope-hygiene packet before commit or cleanup.
- Operator use: Use before staging, committing, or deciding what a closer is allowed to touch.
- Command: `python -m nexus_gate.loops.runner --root . --loop scope-hygiene --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop scope-hygiene --intent "<intent>" --execute --human-authorized --json`

### Script Evolution

- Loop: `script-evolution`
- Group: `Meta Loops`
- Function: Plan and bound a generated script so the script triggers local intelligence instead of duplicating it.
- Operator use: Use when this named loop matches the active gate or wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --execute --human-authorized --json`

### Stale Surface Scan

- Loop: `stale-surface-scan`
- Group: `Maintenance`
- Function: Highlights places where docs or tests may still point at old current-state claims.
- Operator use: Use after version bumps, README edits, or portal/HUD lineage updates.
- Command: `python -m nexus_gate.loops.runner --root . --loop stale-surface-scan --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop stale-surface-scan --intent "<intent>" --execute --human-authorized --json`

### Surface Map

- Loop: `surface-map`
- Group: `Architecture`
- Function: Gives the AI a repo topology map so future patches can target the correct organ.
- Operator use: Use when adding modules, docs, tests, or HUD surfaces.
- Command: `python -m nexus_gate.loops.runner --root . --loop surface-map --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop surface-map --intent "<intent>" --execute --human-authorized --json`

### Validate Promote

- Loop: `validate-promote`
- Group: `Meta Loops`
- Function: Verify candidate patch and stop before commit/push unless the human-authorized outer script performs it.
- Operator use: Use when this named loop matches the active gate or wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --execute --human-authorized --json`

### Wound Indexed Resume

- Loop: `wound-indexed-resume`
- Group: `Meta Loops`
- Function: Emit active wound and resume recommendation.
- Operator use: Use when this loop matches the active gate, wound, or validation need.
- Command: `python -m nexus_gate.loops.runner --root . --loop wound-indexed-resume --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop wound-indexed-resume --intent "<intent>" --execute --human-authorized --json`
