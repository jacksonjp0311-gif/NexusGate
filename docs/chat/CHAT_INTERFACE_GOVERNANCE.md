# Chat Interface Governance

Version: v0.1.0

NEXUS GATE includes multiple chat-like operator surfaces (Electron HUD, PowerShell TUI). This document defines **what they may do**.

## Core contract

```text
human intent -> origin alignment -> route/authority gate -> evidence -> human-authorized durable mutation
```

## Allowed behaviors (chat)

- Collect a human prompt and pass it into governed local routing.
- Render recommendation-only output.
- Surface evidence paths (reports/, state/, docs/) and "next safe move" guidance.
- Run **allowlisted** lanes via the existing relay contract (no arbitrary shell).
- Run HANDOFF scripts **only** when the operator explicitly authorizes `/handoff run`.

## Disallowed behaviors (chat)

- No autonomous repo mutation.
- No git commit/push triggered by model output.
- No arbitrary PowerShell/command execution.
- No secret access beyond the allowlisted read surfaces.

## Required evidence & gates

Before any durable mutation (outside chat):

- `python -m nexus_gate.compiler --root . --json`
- targeted tests for the modified surface

## Claim boundary

This governance document improves operator safety. It does not prove correctness, security, safety, or production readiness.
