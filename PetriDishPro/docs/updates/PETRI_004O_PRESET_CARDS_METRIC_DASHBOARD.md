# PETRI 004O â€” Preset Cards + Metric Dashboard

## Wound
The microscope UI had selectable organism cards, but metrics were still mostly numeric tiles. The entry menu did not mirror the card registry, and cards did not yet change strongly by preset. Drug and antibody testing need a scalable card schema before real datasets are attached.

## Patch
004O adds:

- `config/preset_cards.json` for preset-aware organism, field, intervention, and metric sections.
- `config/metric_cards.json` for chart metadata.
- Electron IPC methods for preset and metric card registries.
- `dashboardCards.js`, an adaptive overlay that renders preset cards, intervention cards, metric charts, and emergent condition cards.
- An entry menu wrapper that mirrors the same card registry before showing the original console menu.

## Data-source direction
- Small-molecule activity slots: ChEMBL / PubChem.
- Antimicrobial interpretation slots: EUCAST / CLSI.
- Antibody/antigen structure slots: RCSB PDB / future internal datasets.
- Organism metadata slots: BacDive / EcoCyc / BsubCyc / SGD / CDC Acanthamoeba.

## Claim boundary
Drug and antibody cards are simulation controls and data slots only. They are not clinical recommendations, susceptibility interpretations, treatment guidance, wet-lab proof, or biosafety evidence.
