# NEXUS GATE Goal Lock

NEXUS GATE is not a generic code generator.

The goal is:

```text
Build a governed transfer boundary between agent frameworks.
```

The architecture lanes are:

```text
adapter
schema
codec
authority
hot route
cold evidence
wound route
replay
disengagement
ledger
compiler
```

## Stay on Track

Do not add code unless it advances one of these lanes.

Do not grow installer complexity unless it reduces user friction.

Do not grow command complexity unless it improves validation, compression, or governed transfer.

Do not add autonomous authority.

Do not add write authority without explicit authority contracts.

## Current Build Track

```text
v0.1.5 = strict compiler + cold evidence/wound routing
v0.1.6 = compression, packing, goal lock
v0.1.7 = adapter registry + demo adapter
v0.2.0 = first bounded bridge runtime
```

Boundary: the goal lock improves project focus. It does not prove correctness, safety, security, or production readiness.
