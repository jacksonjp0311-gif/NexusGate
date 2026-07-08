# NEXUS AI Toolbelt

The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.
It lets ChatGPT/Codex recommend useful local loops without granting direct repo authority.

Boundary: the toolbelt is an index and packet emitter only. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.

## Fast Start

```powershell
python -m nexus_gate.loops.toolbelt --root . --json
python -m nexus_gate.loops.runner --root . --loop toolbelt-start --intent "<intent>" --execute --human-authorized --json
python -m nexus_gate.loops.runner --root . --loop toolbelt-dashboard --intent "<intent>" --execute --human-authorized --json
```

## Toolbelt Groups

### Orient

- Purpose: Rehydrate from repo truth, see status, and select the next local loop.
- Chain: `repo-radar -> toolbelt-index -> next-action-router`
- Ready: `true`
- Loops: `repo-radar, ai-orchestrator-preflight, toolbelt-index, toolbelt-dashboard, next-action-router, local-oracle`

### Plan

- Purpose: Turn intent into architecture, patch plan, test plan, and bounded build chain.
- Chain: `idea-forge -> architecture-sketch -> patch-plan -> test-strategy`
- Ready: `true`
- Loops: `idea-forge, architecture-sketch, patch-plan, test-strategy, creative-build-chain, pair-programming-brief`

### Debug

- Purpose: Narrow failures into wounds and select the smallest healing surface.
- Chain: `debug-lens -> wound-indexed-resume -> compiler-wound-focus`
- Ready: `true`
- Loops: `debug-lens, wound-indexed-resume, compiler-wound-focus, debug-recovery-chain, failure-intelligence, friction-detector`

### Hygiene

- Purpose: Keep scope clean, claims bounded, stale surfaces visible, and authority intact.
- Chain: `scope-hygiene -> boundary-scan -> claim-boundary-audit`
- Ready: `true`
- Loops: `scope-hygiene, claim-boundary-audit, boundary-scan, stale-surface-scan, risk-register, dependency-preflight`

### Ship

- Purpose: Validate, summarize, seal, and prepare human-authorized durable mutation.
- Chain: `bounded-validation -> release-brief -> release-seal -> commit-story`
- Ready: `true`
- Loops: `bounded-validation, release-brief, toolbelt-ship, release-seal, commit-story, continuity-seal`

### Memory

- Purpose: Preserve continuity through handoff packs, session briefs, docs weaving, and memory anchors.
- Chain: `handoff-pack -> session-brief -> memory-anchor -> continuity-seal`
- Ready: `true`
- Loops: `handoff-pack, session-brief, memory-anchor, docs-weaver, continuity-seal, paradise-index`

### UI / HUD

- Purpose: Support the operator surface: loop cards, command palette, UI polish, and code garden maps.
- Chain: `hud-loop-sync -> command-palette -> ui-polish`
- Ready: `true`
- Loops: `hud-loop-sync, command-palette, ui-polish, code-garden-map, surface-map`
