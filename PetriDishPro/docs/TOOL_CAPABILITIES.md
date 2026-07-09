# Tool Capabilities

PetriDishPro is organized around a small set of user-facing tools and internal validation surfaces.

## User-facing tools

| Tool | Purpose |
| --- | --- |
| Electron Microscope HUD | Opens the cyberpunk live microscope interface. |
| Preset selector | Switches between simulation modes such as Microbial Competition, Antibiotic Selection, Biofilm Stress, Antifungal Pressure, and Protist Predation. |
| Organism cards | Displays source-gated organism metadata, behavior proxies, growth/biofilm/stress values, and selectable registry entries. |
| Population curves | Visualizes educational population trend proxies across selected organisms. |
| Density map | Shows a visual proxy for spatial density and particle distribution. |
| Particle State / Registry Receipt | Displays run identity, selected organisms, preset, and artifact-backed state. |
| Metric cards | Tracks simplified metrics such as total cells, diversity, dominance, active organisms, particles, and FPS. |
| Emergent conditions | Summarizes high-level simulation state signals. |
| Drug Lab HUD | Provides an educational overlay for drug-card interaction modeling and response proxies. |
| Validation tests | Runs the project validation suite before claims or release. |
| Latest receipt | Opens the most recent run receipt/artifact for review. |

## Preset families

- Microbial Competition
- Antibiotic Selection
- Cellular Tissue Interaction
- Drug Response Screen
- Antibody Binding Screen
- Antifungal Pressure
- Biofilm Stress
- Protist Predation
- Photosynthetic Mat
- Metric Cards

## Drug Lab boundary

The Drug Lab HUD models educational interaction proxies only. It is not a dosing tool, clinical decision system, susceptibility test, treatment recommendation system, antibody-affinity measurement, wet-lab workflow, or biosafety system.

## Validation philosophy

PetriDishPro follows a receipts-first workflow:

```text
models simulate -> humans validate -> receipts govern claims
```

The project should not make stronger claims than the available source gates, validation output, and receipts support.
