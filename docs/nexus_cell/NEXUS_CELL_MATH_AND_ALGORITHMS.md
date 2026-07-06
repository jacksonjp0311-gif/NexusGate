# NexusCell Math and Algorithms

## Capability Vector

```text
C = [
  fs_read,
  fs_write,
  network,
  secrets,
  registry,
  process_spawn,
  service_install,
  git_write,
  host_mount,
  clipboard,
  gpu
]
```

## Risk Score

```text
R(action) = sum(w_i * C_i) + B + G + N + S
```

Default weights are implemented in `nexus_gate.nexus_cell.risk.DEFAULT_WEIGHTS`.

## Boundary Law

First match wins. All declared match fields are ANDed. Missing fields are wildcards. Default is deny.

## Ledger Hashchain

```text
event_hash_i = SHA256(canonical_json(event_i_without_hashes))
ledger_hash_i = SHA256(event_hash_i || ledger_hash_{i-1})
ledger_hash_0 = SHA256("NEXUS_CELL_GENESIS")
```

## Execution Receipt

```text
receipt_id = SHA256(cell_id || invocation_id || stdout_hash || stderr_hash || ledger_hash)
```

## Return Seal

```text
seal_id = SHA256(origin_image_id || cell_id || state_digest || policy_hash || created_at)
```
