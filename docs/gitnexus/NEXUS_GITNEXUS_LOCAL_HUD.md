# NEXUS GITNEXUS Local HUD v0.5.2

## Decision

The local HUD is the right NexusGate product shape. It should behave like a
native visual organ, not a remote GitNexus web embed.

## v0.5.2 evolution

- Smooth camera easing
- Momentum/inertia for pan, zoom, and rotation
- Dynamic force relaxation
- Hover highlight and connected-neighbor glow
- Click select
- Double-click focus
- Top-file click focus
- FORCE / ORBIT / CIRCLE layout modes
- Animated edge energy
- REFRESH graph reload
- Mini graph uses the same local graph

## Controls

```text
drag                  pan
mouse wheel           zoom
Alt + drag            rotate
Shift + mouse wheel   rotate
double-click node     focus node
FIT / R               fit graph
TURN / [ / ]          rotate graph
+ / -                 zoom
WASD / arrows         pan
SPACE                 pause/resume graph motion
EDGES                 toggle edges
LABELS                toggle labels
CORE                  focus core/python/ui/test files
FORCE/ORBIT/CIRCLE    layout mode cycle
REFRESH               reload local graph JSON
Ctrl+K                search when HUD is open
Esc                   close HUD
```

## Boundary

Evidence-only. No NexusCell policy change. No shell execution from model output.
No remote bridge. No iframe.

## v0.5.2 AI finalizer

AH validation failed on a source-token test, not on runtime syntax. The local HUD
used lowercase layout keys and converted them with `.toUpperCase()` at render
time. The test expected explicit source labels `FORCE`, `ORBIT`, and `CIRCLE`.

AI adds `LAYOUT_LABELS` and routes the layout button through those explicit
labels without changing the HUD behavior.
