# NEXUS Loop Cards

NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.
They preserve the loop registry as data and present each loop as a human-readable card.

Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.

## Card Surfaces

- `state/loops/nexus_loop_cards.v0.9.1B.json`
- `state/loops/nexus_loop_cards_latest.json`
- `python -m nexus_gate.loops.cards --root . --json`
- Spiral Core Portal option `[14] Nexus Loops / Cards`

## Cards

### Failure Intelligence

- Loop: `failure-intelligence`
- Function: Read failure surfaces so the next closer heals the active wound rather than drifting.
- Operator use: Use after a failed gate to identify the next exact repair target.
- Command: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --json`
- Human authorization required: `false`

### Reflective Validation

- Loop: `reflective-validation`
- Function: Run compile/test/compiler gates and convert failures into compact wound intelligence.
- Operator use: Use after a patch when you need gate evidence and wound capture.
- Command: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --json`
- Human authorization required: `true`

### Rhp Core

- Loop: `rhp-core`
- Function: Rehydrate repository origin before patching, compounding, or agent continuation.
- Operator use: Use first when resuming from chat, memory, or a dirty session.
- Command: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --json`
- Human authorization required: `false`

### Script Evolution

- Loop: `script-evolution`
- Function: Shape generated scripts so ChatGPT/Codex work through local governed intelligence instead of loose patches.
- Operator use: Use before generating a new All-One closer or code-changing script.
- Command: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --json`
- Human authorization required: `false`

### Validate Promote

- Loop: `validate-promote`
- Function: Validate a candidate patch and stop before durable mutation unless a human-authorized outer script promotes it.
- Operator use: Use as the final local validation loop before commit/push authority.
- Command: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --json`
- Human authorization required: `true`
