# PETRI 004P â€” Card Stack Real Data UI

## Wound
004O added metric charts and emergent-condition cards, but the dashboard still needed a better operator structure:

- metrics needed to stack in the bottom-left corner,
- the particle-state / registry receipt needed to be human readable,
- emergent conditions were visually cut off,
- organism cards needed more source-gated science metadata,
- drug and antibody screens needed data-gated card slots before real-data adapters are added.

## Patch
004P adds a source-gated registry and dashboard layer:

- metrics stack vertically in the bottom-left panel,
- registry receipt becomes human-readable rows,
- emergent conditions get their own scrollable panel,
- additional organism cards are added as educational proxies with source gates,
- preset-specific card models are added for microbial competition, antibiotic selection, drug response, antibody binding, and tissue interaction,
- the entry menu mirrors the same card architecture.

## Claim boundary
This remains exploratory simulation. ChEMBL, EUCAST, CLSI, RCSB, BacDive, BioCyc, and SGD references define future data-adapter provenance slots, not clinical/treatment/wet-lab claims.
