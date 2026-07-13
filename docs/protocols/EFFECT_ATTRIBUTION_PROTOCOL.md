# Effect Attribution Protocol

Effect attribution is action-window-associated unless process-level file access is instrumented.

The effect receipt compares pre-execution and post-execution snapshots:

- relative path
- existence
- content hash
- size
- canonical/generated classification

It reports:

- added files
- deleted files
- modified files
- pre-existing dirty files
- already-dirty files changed again
- expected canonical writes
- unexpected canonical writes
- expected generated writes
- unexpected generated writes

Unexpected canonical writes create confounder pressure and block durable learning.
