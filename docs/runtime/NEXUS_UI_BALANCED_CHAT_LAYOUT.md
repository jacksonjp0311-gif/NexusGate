# Nexus UI Balanced Chat Layout

Version: v0.1.6

Purpose: rebalance the operator HUD so the center chat/output column sits visually centered between equal side rails.

Human layout request:

```text
remove the Lane Context box
move the chat inward so the chat box is more centered
make the health-score side use the same space as the other side
leave an empty left-side spacer after removal, about the screenshot size
```

Boundary: UI layout patch only. It does not change authority, policy, model routing, health scoring, telemetry scoring, memory, NexusCell execution, or governance.

## Wiring Lock

The renderer patch is not active unless the detected HTML entrypoint is committed with:

```html
<script src="./nexus_ui_layout_balance_patch.v0.1.6.js" data-nexus-ui-layout="balanced-chat-v0.1.6"></script>
```

A future script must stage the exact HTML file listed in `state/ui/nexus_ui_balanced_chat_layout.v0.1.6.json`, not a wildcard such as `*.htm`, because missing pathspecs can fail while leaving the intended HTML file unstaged.
