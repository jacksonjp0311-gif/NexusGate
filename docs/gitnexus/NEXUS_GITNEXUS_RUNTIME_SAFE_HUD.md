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