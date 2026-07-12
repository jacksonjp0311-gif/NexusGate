# Causal Action Receipt Loop v2.6.2

NEXUS now treats governed action as a receipt-backed lifecycle:

recommendation -> human authorization -> registered execution -> effect capture -> validation -> bounded learning

Each transition is explicit. No stage may infer the next stage from success, process existence, stdout, or prior intent.

The first implementation runs in shadow mode. `evolve` may create a recommendation receipt and verify the action ledger, but it does not authorize or execute.

The governing law:

```text
TIME WITHOUT CAUSALITY IS HISTORY.
ACTION WITHOUT AUTHORIZATION IS INVALID.
OUTCOME WITHOUT EXECUTION PROOF IS CORRELATION.
SUCCESS WITHOUT VALIDATION IS UNCONFIRMED.
LEARNING WITHOUT RECEIPTS IS DRIFT.
NO RECEIPT, NO LEARNING.
```

Claim boundary: causal action receipts provide local governed attribution evidence. They do not prove consciousness, general intelligence, scientific truth, security, production readiness, autonomous authority, or globally correct causal inference.
