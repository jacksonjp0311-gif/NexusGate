# PETRI 004B â€” Organism / Cell Visual Model

## Goal
The dish should read visually as many organisms/cells rather than a few glowing blobs.

## What changed
- Added a renderer overlay that synthesizes many discrete cell glyphs.
- Organism morphology maps to microbe style:
  - `ecoli_like` and `bacillus_like` -> rods
  - `yeast_like` -> budding yeast circles
  - `predator_microbe` -> amoeboid/pseudopod form
  - `resistant_variant` -> cocci
- The overlay is inferred from current organism cards and population values.
- This is an operator-surface rendering refinement only.

## Claim boundary
Exploratory simulation only. This patch improves visual interpretation of the dish and does not elevate scientific claim level.
