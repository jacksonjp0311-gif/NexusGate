# NEXUS GITNEXUS Scope Switch v0.3.9

## Purpose

Scope must not lock the operator out. The default GITNEXUS view is ALL.

## Modes

- ALL: show every graph artifact, including generated files, reports, state, ledgers, tests, and debug exhaust.
- CORE: temporarily hide generated/debug exhaust from the visible HUD.

## Boundary

Nothing is deleted. CORE is only a visibility mode. The operator can return to
ALL from the HUD switch or with:

```js
window.gitnexusScopeAll()
```