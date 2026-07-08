# NEXUS Loop Cards

NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.
v0.9.2 expands cards into AI-callable local loop fabric surfaces.

Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.

## Card Surfaces

- `state/loops/nexus_loop_cards.v0.9.2.json`
- `state/loops/nexus_loop_cards_latest.json`
- `python -m nexus_gate.loops.cards --root . --json`
- Spiral Core Portal option `[14] Nexus Loops / Cards`

## Cards

### Ai Orchestrator Preflight

- Loop: `ai-orchestrator-preflight`
- Function: Give AI local context before selecting a loop.
- Command: `python -m nexus_gate.loops.runner --root . --loop ai-orchestrator-preflight --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop ai-orchestrator-preflight --intent "<intent>" --execute --human-authorized --json`

### Bounded Validation

- Loop: `bounded-validation`
- Function: Run compile, bounded tests, compiler.
- Command: `python -m nexus_gate.loops.runner --root . --loop bounded-validation --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop bounded-validation --intent "<intent>" --execute --human-authorized --json`

### Compiler Wound Focus

- Loop: `compiler-wound-focus`
- Function: Focus exact compiler failed gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop compiler-wound-focus --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop compiler-wound-focus --intent "<intent>" --execute --human-authorized --json`

### Docs Doctrine Preflight

- Loop: `docs-doctrine-preflight`
- Function: Read README and script doctrine.
- Command: `python -m nexus_gate.loops.runner --root . --loop docs-doctrine-preflight --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop docs-doctrine-preflight --intent "<intent>" --execute --human-authorized --json`

### Failure Intelligence

- Loop: `failure-intelligence`
- Function: Read failure surfaces for next wound.
- Command: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop failure-intelligence --intent "<intent>" --execute --human-authorized --json`

### Hud Loop Sync

- Loop: `hud-loop-sync`
- Function: Regenerate loop cards.
- Command: `python -m nexus_gate.loops.runner --root . --loop hud-loop-sync --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop hud-loop-sync --intent "<intent>" --execute --human-authorized --json`

### Impact Map

- Loop: `impact-map`
- Function: Map patch impact through GITNEXUS.
- Command: `python -m nexus_gate.loops.runner --root . --loop impact-map --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop impact-map --intent "<intent>" --execute --human-authorized --json`

### Reflective Validation

- Loop: `reflective-validation`
- Function: Run compile/test/compiler gates.
- Command: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop reflective-validation --intent "<intent>" --execute --human-authorized --json`

### Release Seal

- Loop: `release-seal`
- Function: Final evidence before commit/push.
- Command: `python -m nexus_gate.loops.runner --root . --loop release-seal --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop release-seal --intent "<intent>" --execute --human-authorized --json`

### Rhp Core

- Loop: `rhp-core`
- Function: Rehydrate repository origin before patching.
- Command: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" --execute --human-authorized --json`

### Script Evolution

- Loop: `script-evolution`
- Function: Shape generated scripts through governed intelligence.
- Command: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" --execute --human-authorized --json`

### Validate Promote

- Loop: `validate-promote`
- Function: Validate before promotion.
- Command: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --execute --human-authorized --json`

### Wound Indexed Resume

- Loop: `wound-indexed-resume`
- Function: Emit active wound and resume recommendation.
- Command: `python -m nexus_gate.loops.runner --root . --loop wound-indexed-resume --intent "<intent>" --json`
- Execute: `python -m nexus_gate.loops.runner --root . --loop wound-indexed-resume --intent "<intent>" --execute --human-authorized --json`
