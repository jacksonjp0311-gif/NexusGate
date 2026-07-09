# PETRI 005N - Missing Metric Card ID Seal

## Wound
005M reduced strict tests to one exact failure:

`metrics["cards"]` did not include a card whose `id` is `antibody_occupancy_proxy`.

## Patch
005N adds dual-shape metric compatibility for:

- `antibody_occupancy_proxy`,
- `binding_occupancy`,
- `antibody_binding_proxy`,
- `igg_opsonization_proxy`.

The metric registry still keeps the keyed `metrics` object and the list-shaped `cards` array.

## Claim boundary
Compatibility only. These are educational proxy metrics, not antibody affinity, neutralization, diagnostic, clinical, wet-lab, or treatment evidence.
