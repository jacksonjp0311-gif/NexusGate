# PETRI 005O - Drug Injection HUD + Preset Organism Selector

## What changed
005O adds the first real interaction UI layer:

- organism cards are rendered collapsed by default,
- each organism card expands open when clicked,
- each checkbox selects/deselects the organism for the active preset,
- preset changes re-render the organism card set,
- a cyber-blue `Drug Injection` button is inserted next to the top controls,
- the button opens a large semi-transparent Drug Interaction Lab HUD,
- the HUD contains drug cards, class/target filters, target organism response rows, dose/exposure/application controls, and a predicted response curve.

## Drug card boundary
Drug cards are educational mechanism proxies. They are not dosing instructions, wet-lab susceptibility outputs, treatment advice, clinical guidance, diagnostic support, antibody-affinity measurements, or biosafety guidance.

## Interaction model
005O uses a simple proxy algorithm:

- selected organisms provide target context,
- drug class/target overlap gives a response score,
- organism biofilm/stress fields dampen response,
- the HUD renders a non-calibrated response curve.

## Next
005P should move from UI proxy response into stronger behavior algorithms:
- motility rules,
- chemotaxis-like gradient seeking,
- biofilm attachment/detachment,
- predator/prey rules,
- drug-gradient pressure fields,
- antibody occupancy fields.
