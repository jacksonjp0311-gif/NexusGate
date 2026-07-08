# NEXUS GITNEXUS Local HUD v0.5.3

## Geometry Analyzer pass

Adds label collision/fade, better initial fit, FAST/SLOW runtime speed, HOT/CHANGED/CORE mode cycling, selected-node path highlighting, mini/full graph parity, better category coloring, and a live geometry analyzer.

## Geometry analyzer outputs

- Pattern
- Density
- Hubs
- Bridge pressure
- Category balance / entropy
- Anisotropy
- Recommendation

## Controls

```text
G                     toggle FAST/SLOW
M                     cycle MODE ALL/HOT/CHANGED/CORE
drag                  pan
mouse wheel           zoom
Alt + drag            rotate
Shift + mouse wheel   rotate
double-click node     focus node
FIT / R               fit graph
TURN / [ / ]          rotate graph
+ / -                 zoom
WASD / arrows         pan
SPACE                 pause/resume motion
REFRESH               reload local graph JSON
Ctrl+K                search when HUD is open
Esc                   close HUD
```

Boundary: evidence-only; no NexusCell policy change; no shell execution from model output; no iframe; no remote bridge.