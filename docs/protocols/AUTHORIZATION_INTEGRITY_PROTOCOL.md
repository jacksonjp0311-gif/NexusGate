# Authorization Integrity Protocol

Human authorization is explicit, single-action, non-delegable, non-reusable evidence.

Execution must revalidate:

- recommendation receipt exists
- authorization receipt exists
- authorization has not expired
- action is not already executed
- command registry entry exists
- command registry entry hash matches the recommended entry
- command registry ID matches the authorization binding
- arguments hash matches
- pre-source epoch matches
- pre-source root matches

Any mismatch blocks execution as `STALE`, `EXPIRED`, or `INVALID`.
