# NexusCell Security Model

NexusCell is local development execution-governance infrastructure.

## Active v0.1 backend

```text
mock
```

The mock runner does not execute payload code. It reads payload metadata, applies the Secret Veil, emits a receipt, and appends the continuity ledger.

## Scaffolded backends

```text
windows_sandbox_ephemeral
hyperv_container
hyperv_vm
```

These are interfaces and scripts only until explicitly enabled and validated.

## Secret Veil

Raw secrets must not appear in payloads, receipts, stdout/stderr, or ledger entries.

## Boundary

```text
NexusCell is local development execution-governance infrastructure.

It is not a production security proof.
It is not a perfect sandbox.
It is not malware-proof.
It is not AGI.
It is not autonomous authority.
It is not a correctness proof.
It is not full rollback until Return Seal backend exists.
It does not replace human authorization.
```
