# Chat Intelligence Routing

Version: v0.1.0

NEXUS GATE routes chat prompts through **role selection** and governed evidence surfaces.

## Roles (Electron)

- FAST / BALANCED: local lightweight recommendation voices.
- DEEP: local deeper recommendation voice.
- TNN: minimal neural surface.
- HANDOFF: operator-mediated ChatGPT/Codex packet mode (no local model authority).

## Routing axes (Geometric Memory Router)

```text
Axis 1: Intent
Axis 2: Evidence
Axis 3: Authority
Axis 4: Context
```

A request is not router-ready until all four axes are populated.

## Offline behavior (required)

If the local model endpoint is unavailable:

- the chat surface must still be responsive
- it must return evidence-forward guidance
- it must not pretend a model response occurred

## Claim boundary

Routing improves controllability; it does not prove correctness, safety, security, or production readiness.
