# NEX Chat Bridge

Version: v0.6.4

## Purpose

The Electron HUD now treats chat as the primary operator interaction surface.

The center panel is simplified into:

```text
NEX AI output
Human chat input
```

The top buffer bar is moved above the chat and animated as an electric-chain collector. When the run completes, the buffer crystallizes into an ice-blue pulse.

## Avatar

The local AI interface avatar is named:

```text
NEX
```

NEX is an interface symbol, not an autonomous authority. When NEX is processing, the AI box glows cyberpunk orange and pulses.

## Chat Semantics

- Enter sends the human message.
- Shift+Enter inserts a new line.
- `/status`, `/feedback`, and other allowlisted slash commands still route through governed lanes.
- Normal chat sends a bounded packet to the NN router role selected in the Reasoning Selector.
- Role selection is UI planning context until the human sends a message.

## Authority Boundary

The chat bridge does not:

- execute model output as shell
- grant model authority
- mutate files from model output
- read secrets
- write external APIs
- bypass NEXUS gates

NEX replies are recommendation context only. Durable mutation still requires human authorization and repo gates.

