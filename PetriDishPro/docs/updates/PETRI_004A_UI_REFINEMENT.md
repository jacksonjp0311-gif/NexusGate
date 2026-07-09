# PETRI 004A â€” Electron Microscope UI Refinement

## Scope

004A resumes from the sealed 003E validation contract and refines the operator surface only. It does not rewrite the simulation kernel.

## Healed wounds

- organism cards rendering `undefined` instead of names/kinds
- blank/low-signal population curve panel
- crude square heatmap presentation
- missing run archive / artifact browser surface

## Added

- schema normalization adapter in Electron renderer
- dominant organism display by resolved name
- circular microscope dish with glow, pan, zoom, reset, and optional grid overlay
- metrics chips
- organism population cards with bars
- archive list and artifact opener bridge

## Claim boundary

Exploratory simulation only. Not clinical, diagnostic, wet-lab, treatment, biosafety, or regulatory evidence.
