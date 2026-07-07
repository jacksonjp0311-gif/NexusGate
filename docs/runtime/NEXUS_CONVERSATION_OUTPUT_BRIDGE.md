# NEXUS Conversation Output Bridge v0.2.1B

This bridge strengthens normal-chat handling.

## Behavior

- Normal chat phrases such as `you there`, `hey`, and `hi` render conversationally.
- Partial audit cards are recognized even if `Human Authorization` is absent.
- Stale engineering-context answers are replaced when the user submitted plain chat.
- Operator/system tasks still keep recommendation-only governance.

## Closed wounds

- `Observation / Recommendation / Risk` no longer survives for simple chat.
- Stale â€œnext safe engineering moveâ€ responses no longer override greetings.