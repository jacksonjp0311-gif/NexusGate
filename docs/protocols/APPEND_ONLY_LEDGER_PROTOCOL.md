# Append-Only Ledger Protocol

NEXUS append-only ledgers are JSONL hash chains.

Append flow:

1. Acquire a bounded lock.
2. Verify the current chain tail.
3. Construct the event with `previous_event_hash`.
4. Compute `event_hash`.
5. Append one complete JSON line.
6. Flush and fsync.
7. Read the tail and verify the appended hash.
8. Release the lock.

The verifier reports chain length, tail hash, malformed rows, hash mismatches, duplicate event IDs, and fork evidence.

Latest files are pointers. Ledgers and immutable state directories are durable memory.
