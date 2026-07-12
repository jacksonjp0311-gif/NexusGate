# Epoch Integrity Seal Protocol

## Protocol

1. Gather tracked canonical source surfaces from README, AGENTS, docs, tests, scripts, policy, chatgpt, pyproject, and `nexus_gate/`.
2. Hash each surface as `sha256(path + NUL + file_sha256)`.
3. Build a deterministic Merkle root from sorted leaf hashes.
4. Compute:

```text
epoch_id = SHA256(source_root + parent_epoch_id + runtime_contract_version)
```

5. Write immutable epoch packets under `state/epochs/<epoch_id>/`.
6. Update `state/latest_epoch_pointer.json`.
7. Append a hash-linked event to `ledger/epoch_chain.jsonl`.
8. Treat Git commit SHA as advisory post-source attestation, not primary epoch identity.

## Outputs

- `reports/nexus_epoch_integrity_seal_latest.json`
- `state/latest_epoch_pointer.json`
- `state/epochs/<epoch_id>/epoch_manifest.json`
- `state/epochs/<epoch_id>/origin_packet.json`
- `state/epochs/<epoch_id>/gate_index.json`
- `ledger/epoch_chain.jsonl`

## Law

Immutable time before temporal learning.

The epoch seal may orient graphs, memory, routes, and future pruning. It may not execute, self-authorize, erase evidence, or certify safety.

