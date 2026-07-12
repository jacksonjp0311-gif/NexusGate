# Source Epoch and Observation Protocol

Source Epoch:

- Changes only when canonical source content, runtime contract, or schema compatibility changes.
- Uses `working_tree_source_root` and `tracked_source_root`.
- Includes relevant untracked source files.
- Excludes generated runtime caches, reports, ledgers, build output, caches, binaries, and neural visualization runtime state.

Observation Event:

- May be produced repeatedly for the same Source Epoch.
- Appends to `ledger/epoch_observations.jsonl`.
- Never fabricates a new developmental epoch by itself.

Learning admissibility:

- `sealed_clean` -> `admissible`
- `sealed_working_tree` -> `working_tree_only`
- `dehydrated`, `stale`, `invalid`, `invalid_epoch_collision` -> not learnable
