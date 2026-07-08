# Chat Interface Walkthrough

Version: v0.1.0

## Electron HUD quick test

1. Start the desktop portal or Electron HUD.
2. Verify the **telemetry HUD** shows CPU/RAM and an Ollama status.
3. Send: `hello`
4. Expected:
   - a greeting response
   - status becomes `stable`

## If chat is "blocked"

Most common blockers:

- Local model endpoint unreachable (WinError 10061 / connection refused).
- Python router/report path missing.

Operator actions:

- Use `/run status` to verify local lanes.
- Switch to HANDOFF if you want to proceed without local model calls.
- Run `python -m nexus_gate.compiler --root . --json` before any durable mutation.

## Claim boundary

This walkthrough is operational guidance only.
