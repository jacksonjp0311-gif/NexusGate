# PETRI 004Q â€” Preset Schema Compatibility Seal

## Wound
004P correctly added preset-aware card and metric dashboard content, but it changed the top-level schema identifiers in:

- `config/preset_cards.json`
- `config/metric_cards.json`

The existing 004O tests intentionally treat those schema identifiers as stable registry contracts:

- `PETRI_PRESET_CARD_REGISTRY.v0.4o`
- `PETRI_METRIC_CARD_REGISTRY.v0.4o`

## Patch
004Q preserves the 004P content but restores the stable 004O schema identifiers. The 004P upgrade is retained as `content_version: "004P"` and a `compatibility_seal` block.

## Claim boundary
This is a schema compatibility seal only. It does not change the biological model, drug-response model, antibody model, clinical claim level, or wet-lab evidence status.
