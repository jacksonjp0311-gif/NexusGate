# NEXUS AI Toolbelt

The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.
v0.9.7 adds Toolbelt Cockpit Output: human cockpit by default, JSON packet on request.

Boundary: read-only operator cockpit. No autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.

## Commands

```powershell
.\scripts\nexus.ps1 toolbelt
.\scripts\nexus.ps1 toolbelt-json -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-next -Tag "<intent>"
.\scripts\nexus.ps1 toolbelt-ship -Tag "<intent>"
```

## Default Process

```text
Start: toolbelt-start -> toolbelt-dashboard -> next-action-router
Build: idea-forge -> architecture-sketch -> patch-plan -> test-strategy
Debug: debug-lens -> wound-indexed-resume -> compiler-wound-focus
Ship: scope-hygiene -> boundary-scan -> release-brief -> release-seal
Continuity: handoff-pack -> session-brief -> memory-anchor -> continuity-seal
```

## Current Recommendation

- Loop: `scope-hygiene`
- Reason: working tree has local changes
- Next command: `.\scripts\nexus.ps1 meta-loop -Loop scope-hygiene -Tag "unit"`

## Groups

### Orient

- Purpose: Rehydrate, see status, and route next action.
- Chain: `repo-radar -> toolbelt-cockpit -> toolbelt-next`
- Ready: `true`

### Plan

- Purpose: Turn intent into architecture, patch plan, and tests.
- Chain: `idea-forge -> architecture-sketch -> patch-plan -> test-strategy`
- Ready: `true`

### Debug

- Purpose: Narrow failures into wounds.
- Chain: `debug-lens -> wound-indexed-resume -> compiler-wound-focus`
- Ready: `true`

### Hygiene

- Purpose: Keep scope, claims, stale surfaces, and authority clean.
- Chain: `scope-hygiene -> boundary-scan -> claim-boundary-audit`
- Ready: `true`

### Ship

- Purpose: Validate, summarize, seal, and prepare human-authorized mutation.
- Chain: `bounded-validation -> release-brief -> release-seal -> commit-story`
- Ready: `true`

### Memory

- Purpose: Preserve continuity.
- Chain: `handoff-pack -> session-brief -> memory-anchor -> continuity-seal`
- Ready: `true`

### UI / HUD

- Purpose: Support cards, command palette, UI polish, and code garden maps.
- Chain: `hud-loop-sync -> command-palette -> ui-polish`
- Ready: `true`
