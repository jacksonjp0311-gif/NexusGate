# Epoch Integrity Seal Design

NEXUS GATE v2.6.1 separates source identity from Git commit identity.

Generated evidence can be committed after it is produced, so a report cannot reliably contain the hash of the future commit that will contain that report. The Epoch Integrity Seal fixes that by making the source Merkle root the primary identity and treating the commit SHA as advisory attestation.

```text
canonical source surfaces
  -> per-file hashes
  -> source Merkle root
  -> parent epoch + runtime contract
  -> epoch_id
  -> immutable epoch directory
  -> append-only epoch chain
```

The latest pointer is a convenience surface only. Durable memory lives in `state/epochs/<epoch_id>/` and `ledger/epoch_chain.jsonl`.

## Epoch States

- `sealed_clean`: required surfaces exist and no canonical source surfaces are dirty.
- `sealed_working_tree`: required surfaces exist and canonical source surfaces are changing.
- `dehydrated`: required source or doctrine surfaces are missing.
- `stale`: reserved for future cross-epoch invalidation.
- `invalid`: reserved for schema or chain violations.

## Boundary

Epoch integrity is identity evidence, not correctness proof. It cannot authorize mutation, skip final evolve, prune files, or replace human command.

