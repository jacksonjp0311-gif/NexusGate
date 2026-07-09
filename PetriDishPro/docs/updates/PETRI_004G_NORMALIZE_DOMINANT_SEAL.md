# PETRI 004G â€” Normalize Dominant Seal

## Wound
004F passed compile, unit tests, and demo receipts, then failed the static schema-adapter wound check because `function normalizeDominantName(run)` was still not visible in `electron/renderer/app.js`.

## Patch
004G patches only the missing compatibility function and rechecks the static contract before rerunning tests.

## Claim boundary
This is a UI/schema compatibility seal only. It does not change biological model semantics or scientific claim level.
