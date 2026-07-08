# Chat Operator Surfaces

Version: v0.1.0

This document names the chat-facing surfaces and their intended meaning.

## Electron HUD

Primary file surfaces:

- `electron/main.js` — IPC boundary + allowlists + hidden local backend bootstrap.
- `electron/preload.js` — exposes a minimal `window.nexus` API (readSurface, runLane, askNex, telemetry).
- `electron/renderer/index.html` — layout + script wiring.
- `electron/renderer/renderer.js` — runtime UI logic, lane relay, chat send/stop, telemetry HUD.
- `electron/renderer/nexus_conversation_output_bridge.v0.2.1f.js` — transcript-aware chat output repair.
- `electron/renderer/nexus_ui_center_chat_repair.v0.1.6l.css` — balanced chat layout.

Operator affordances:

- Role select (FAST/BALANCED/DEEP/TNN/HANDOFF)
- Governed lane relay: `/run <lane>` (only allowlisted lanes)
- HANDOFF script bridge: `/handoff run` (explicit operator authorization required)

## PowerShell TUI

- `scripts/nexus.ps1 tui` — terminal operator HUD.

## Boundaries

```text
Selection is not authority.
Chat is not commit.
UI is not mutation.
```
