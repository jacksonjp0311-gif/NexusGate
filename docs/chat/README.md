# docs/chat — NEXUS GATE Chat Surface

Version: v0.1.0

This folder contains the **chat interface governance and operator contracts** for the NEXUS GATE Electron HUD and terminal surfaces.

## Boundary

NEXUS GATE chat is a **recommendation surface**.

```text
Models recommend; humans authorize durable mutation.
Chat text is not authority.
No chat UI may grant repo write authority.
No chat UI may grant arbitrary shell authority.
```

## Start Points

- `CHAT_INTERFACE_GOVERNANCE.md` — what the chat system is allowed to do.
- `CHAT_OPERATOR_SURFACES.md` — what panels/inputs exist and what they mean.
- `CHAT_INTELLIGENCE_ROUTING.md` — how prompts are routed (role, evidence, authority).
- `CHAT_INTERFACE_WALKTHROUGH.md` — operator walkthrough / troubleshooting.
- `CHAT_PERFORMANCE_METRICS.md` — what "working" means (latency, failure modes, offline behavior).
- `CHAT_OPERATION_CONTRACT.md` — the contract that binds operator + system.
