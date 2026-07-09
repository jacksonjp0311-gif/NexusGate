# PETRI 004C â€” Configured Science Microscope

## Wound
The 004A interface was cleaner, but the dish still looked like a field heatmap or four soft blobs. The toxin view also exposed a square overlay wound. That does not match the product goal: the center panel should read as a Petri dish containing many organisms/cells.

## Patch
004C introduces a configuration-driven microscope workbench.

- Adds `config/petri_science_config.v0.4c.json`.
- Replaces the Electron renderer with a config-aware microscope.
- Clips field overlays to a circular dish.
- Keeps field layers below organism/cell morphology.
- Draws discrete morphology proxies:
  - rods for E. coli-like and Bacillus-like organisms,
  - budding circles for yeast-like organisms,
  - amoeboid predator-like cells,
  - cocci for resistant variants.
- Adds sliders for cell density, cell scale, and field opacity.
- Adds a science config panel so the operator can see the assumptions.

## Claim boundary
This is still exploratory simulation and visualization only. The morphology layer is a scientifically-inspired proxy, not microscopy evidence, diagnosis, species identification, wet-lab result, treatment guidance, or biosafety evidence.
