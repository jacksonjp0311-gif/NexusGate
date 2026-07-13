# NEX Inner Communication Protocol

NEX organs communicate by typed messages under `ledger/nex_inner_messages.jsonl`.

Reliability:

```text
q(m) = provenance * verification * freshness * confidence
```

Authority is not part of reliability. Message budgets, hop limits, payload hashes, message hashes, duplicate detection, and replay verification prevent uncontrolled self-amplification.
