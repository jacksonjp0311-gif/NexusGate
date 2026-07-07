# NEXUS Conversation Output Bridge v0.2.1A

This bridge separates normal chat from operator/system tasks.

## Behavior

- Normal human chat renders as conversational NEX output.
- Operator commands keep recommendation-only governance format.
- Repo/tool mutation remains gated.
- Stale selector event spam is suppressed when it conflicts with the submitted role.

## Closed wounds

- Robotic output such as `Observation / Recommendation / Risk / Human Authorization` no longer dominates greetings and short normal chat.
- A stale `FAST selected` event is removed when the submitted role is not FAST.