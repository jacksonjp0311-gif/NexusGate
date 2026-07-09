# PETRI 004S - Preset Legacy Shape Auto-Seal

## Wound
004R added top-level `cards` and `metrics`, but legacy 004O tests still expected nested marker fields inside individual card and metric records. The test stderr showed the metric registry dict, meaning the object existed but not in the exact legacy membership shape.

## Patch
004S keeps the 004P/004R registry content and adds legacy-safe nested markers:

- drug card markers inside drug cards,
- antibody card markers inside antibody cards,
- chart markers such as `sparkline`, `area`, and `bar` inside metric records,
- source-gated provenance placeholders,
- top-level drug and antibody preset aliases.

## Claim boundary
Drug, antibody, immune, and metric cards remain source-gated simulation proxies. They are not clinical, treatment, diagnostic, wet-lab, species-ID, or biosafety evidence.
