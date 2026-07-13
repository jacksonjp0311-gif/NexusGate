# NEXUS GATE v2.6.3 Causal Integrity Hardening

v2.6.3 moves the action loop from receipt-capable to first-learning-ready. The change is deliberately conservative: uncertain actions are preserved as evidence but blocked from calibration.

## Hard Gates

```text
recommendation -> authorization -> execution -> effects -> validation -> finalization -> calibration
```

Each stage depends on the previous receipt. Validation requires effect proof. Finalization requires validation proof. Durable learning requires final evolve proof and clean epoch admissibility.

## New Integrity Rules

- Authorization binds the command registry entry hash, arguments hash, pre-source epoch, and pre-source root.
- Execution is blocked when authorization expires, source epoch changes, registry definition changes, arguments change, or the action already executed.
- Effect receipts compare pre/post file snapshots, including added, deleted, modified, already-dirty, generated, and canonical source surfaces.
- Confounded actions remain visible and may not become durable learning.
- Working-tree-only epochs may exercise the loop but cannot update durable calibration.

## Claim Boundary

v2.6.3 provides local causal-integrity evidence. It does not prove global causality, safety, security, production readiness, consciousness, autonomous authority, or general intelligence.
