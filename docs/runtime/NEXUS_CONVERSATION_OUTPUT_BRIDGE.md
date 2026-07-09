# NEXUS Conversation Output Bridge v0.2.1B

This bridge strengthens normal-chat handling.

## Behavior

- Normal chat phrases such as `you there`, `hey`, and `hi` render conversationally.
- When model output arrives in **audit-card format** (`Observation / Recommendation / Risk / Human Authorization`) *and* the user submitted plain chat, the bridge converts it into a **human reply**.
  - It uses the Recommendation as the main answer.
  - It adds a short `Why:` derived from Observation/Risk (high-level; no hidden chain-of-thought).
  - It can optionally surface a short `Risk:` line.
- Stale engineering-context canned answers are replaced when the user submitted plain chat.
- Operator/system tasks keep recommendation-only governance.

## Closed wounds

- `Observation / Recommendation / Risk` no longer survives for simple chat.
- Stale â€œnext safe engineering moveâ€ responses no longer override greetings.