# NEX Shell Relay Mode

Version: v0.7.3

## Purpose

NEX should let the human operate governed local lanes from the chat surface instead of manually living in PowerShell.

PowerShell remains the hidden execution substrate. The human-facing workflow becomes chat-first.

## Commands

- `/run status`
- `/run interconnect`
- `/run feedback`
- `/run compact`
- `/run pack`

Legacy slash lanes such as `/status` remain supported.

## Output Contract

Every relay result is returned as a compact machine-efficient report:

- What ran
- Result
- Exit code
- Human-readable meaning
- Evidence
- Next allowed action
- Boundary

## Governance Boundary

Shell relay mode does not allow arbitrary shell.

It only runs Electron allowlisted NEXUS lanes through the existing hidden bridge.

Model output cannot execute tools, mutate repo files, promote memory, or grant authority.
