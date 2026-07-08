# NEXUS GITNEXUS Runtime-Safe HUD v0.4.1

## Purpose

v0.4.0 restored the visible GITNEXUS HUD, but it still acted too much like a
global runtime layer. v0.4.1 isolates GITNEXUS so it does not interfere with the
main NexusGate runtime.

## Changes

- One active GITNEXUS asset pair only:
  - `nexus_gitnexus_standalone_hud.v0.4.1.css`
  - `nexus_gitnexus_standalone_hud.v0.4.1.js`
- Mini dock stays simple and animated.
- Full HUD render loop runs only while the full HUD is open.
- Keyboard controls only affect GITNEXUS while the full HUD is open.
- Ctrl+K opens GITNEXUS search.
- No document-wide text sanitizing or broad page mutation.
- ALL/CORE remains a view toggle, not a lockout.

## Boundary

GITNEXUS remains evidence-only. It does not change NexusCell policy, execute
shell commands, or grant autonomous mutation authority.

## v0.4.1 AE finalizer

AD failed before validation because PowerShell `-like` interpreted `[` in
`*html[idx*` as a wildcard character class. AE replaces that self-check with
`.Contains(...)`.

The active bridge test now uses direct string counts:

- active: `nexus_conversation_output_bridge.v0.2.1f.js`
- inactive: `v0.2.1a` through `v0.2.1e`
