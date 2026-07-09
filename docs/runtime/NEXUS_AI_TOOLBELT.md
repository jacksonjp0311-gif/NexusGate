# NEXUS AI Toolbelt

The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.
It lets ChatGPT/Codex recommend useful local loops without granting direct repo authority.

Boundary: the toolbelt is an index and packet emitter only. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.

## Fast Start

```powershell
.\scripts\nexus.ps1 toolbelt
.\scripts\nexus.ps1 toolbelt-start -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-next -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-ship -Tag "<intent>"
```

```bash
bash scripts/nexus.sh toolbelt "<intent>"
bash scripts/nexus.sh toolbelt-next "<intent>"
```

## Default Process

```text
Start      -> toolbelt-start -> toolbelt-dashboard -> next-action-router
Build      -> idea-forge -> architecture-sketch -> patch-plan -> test-strategy
Debug      -> debug-lens -> wound-indexed-resume -> compiler-wound-focus
Ship       -> scope-hygiene -> boundary-scan -> release-brief -> release-seal
Continuity -> handoff-pack -> session-brief -> memory-anchor -> continuity-seal
```

## Toolbelt Groups

### Orient

- Purpose: Rehydrate, see status, and route next action.
- Chain: `repo-radar -> toolbelt-console -> toolbelt-next`
- Ready: `true`
- Loops: `repo-radar, toolbelt-index, toolbelt-console, toolbelt-dashboard, toolbelt-next, next-action-router, local-oracle`

### Plan

- Purpose: Turn intent into architecture, patch plan, and tests.
- Chain: `idea-forge -> architecture-sketch -> patch-plan -> test-strategy`
- Ready: `true`
- Loops: `idea-forge, architecture-sketch, patch-plan, test-strategy, creative-build-chain, pair-programming-brief`

### Debug

- Purpose: Narrow failures into wounds.
- Chain: `debug-lens -> wound-indexed-resume -> compiler-wound-focus`
- Ready: `true`
- Loops: `debug-lens, wound-indexed-resume, compiler-wound-focus, debug-recovery-chain, failure-intelligence, friction-detector`

### Hygiene

- Purpose: Keep scope, claims, stale surfaces, and authority clean.
- Chain: `scope-hygiene -> boundary-scan -> claim-boundary-audit`
- Ready: `true`
- Loops: `scope-hygiene, claim-boundary-audit, boundary-scan, stale-surface-scan, risk-register, dependency-preflight`

### Ship

- Purpose: Validate, summarize, seal, and prepare human-authorized mutation.
- Chain: `bounded-validation -> release-brief -> release-seal -> commit-story`
- Ready: `true`
- Loops: `bounded-validation, release-brief, toolbelt-ship, toolbelt-ship-console, release-seal, commit-story, continuity-seal`

### Memory

- Purpose: Preserve continuity.
- Chain: `handoff-pack -> session-brief -> memory-anchor -> continuity-seal`
- Ready: `true`
- Loops: `handoff-pack, session-brief, memory-anchor, docs-weaver, continuity-seal, paradise-index`

### UI / HUD

- Purpose: Support cards, command palette, UI polish, and code garden maps.
- Chain: `hud-loop-sync -> command-palette -> ui-polish`
- Ready: `true`
- Loops: `hud-loop-sync, command-palette, ui-polish, code-garden-map, surface-map`
