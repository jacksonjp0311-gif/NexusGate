# Semantic Action Chain Protocol

A valid hash chain proves append order, but it does not prove causal correctness.

Semantic verification checks:

- every consumed receipt hash is recomputed;
- the receipt exists at the immutable action path;
- the ledger contains the matching event;
- action IDs and recommendation IDs agree;
- lifecycle stage order is valid;
- no later stage exists without its prerequisite stage.

Required order:

```text
recommendation -> authorization -> execution -> effects -> final_evolve -> validation -> learning
```

Receipt presence alone is not evidence. A tampered receipt must fail closed.
