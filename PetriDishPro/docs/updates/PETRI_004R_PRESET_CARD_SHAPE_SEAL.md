# PETRI 004R â€” Preset Card Shape Seal

## Wound
004Q restored the stable 004O schema IDs, but the legacy 004O tests also require specific top-level registry shapes:

- `config/preset_cards.json` must contain `cards`
- `config/metric_cards.json` must contain `metrics`

004P had evolved the config content but moved away from those top-level keys.

## Patch
004R preserves 004P content and adds compatibility mirrors:

- `cards` top-level preset card registry
- `metrics` top-level metric registry
- drug cards: ampicillin/ciprofloxacin/tetracycline proxies
- antibody cards: neutralizing antibody, IgG opsonization, complement activation
- data adapter slots for compound and structure provenance
- chart contracts for total cells, Shannon diversity, dominance index, resistant fraction, kill curve, dose response, binding occupancy, and escape fraction

## Claim boundary
All drug and antibody cards are source-gated simulation proxies until records with source, ID, assay/method, units, retrieval date, and claim boundary are imported.
