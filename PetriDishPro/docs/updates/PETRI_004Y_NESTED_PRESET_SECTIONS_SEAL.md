# PETRI 004Y - Nested Preset Sections Seal

## Wound
004X added top-level `sections`, but the legacy 004O test checks the nested path:

`cfg['presets']['antibiotic_selection']['sections']`

and expects it to contain `metric_cards`.

## Patch
004Y adds the nested preset section list while preserving the top-level sections and kill_curve_proxy metric.

## Claim boundary
Config contract only. No clinical, wet-lab, diagnostic, treatment, species-ID, or biosafety claims are added.
