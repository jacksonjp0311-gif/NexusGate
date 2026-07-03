# Low-Latency Runtime Discipline

The route path must remain deterministic, cached, and bounded.

Preferred techniques:

```text
precompiled schemas
immutable registry snapshots
capability bitsets
codec cache
authority hash cache
synchronous ledger stubs
async cold evidence processing
deadline-aware mode selection
adapter isolation
```

Heavy work belongs in the cold plane unless synchronous confirmation is required for live authority.