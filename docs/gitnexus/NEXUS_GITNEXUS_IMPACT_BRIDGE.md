# NEXUS GITNEXUS Impact Bridge v0.9.1

## Purpose

The GITNEXUS impact bridge converts local codegraph evidence into a bounded impact packet for NexusGate and NexusCell.

## Boundary

Evidence only. No shell execution. No repository mutation. No git write authority. No model-output authority. No autonomous repair.

## Outputs

- `state/gitnexus/gitnexus_impact_packet_latest.json`
- `reports/gitnexus_impact_report_latest.json`
- `reports/gitnexus_impact_report_latest.md`

## NexusCell

The `gitnexus-impact` lane is a read-only controlled lane that emits the impact packet as evidence. It does not execute arbitrary commands.
