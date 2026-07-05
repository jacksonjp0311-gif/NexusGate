# NEX Reflective Startup

Version: v0.6.5

## Purpose

NEX now opens with exactly one chat message: a greeting.

Startup diagnostics are still available through the telemetry and side panels, but they no longer pollute the opening chat stream.

## Opening Contract

On app open, the visible chat should contain one NEX message:

```text
Hello. I am NEX â€” your bounded reflective intelligence surface.
```

No selector initialization message, TUI fallback warning, stale model error, or prior output should appear as opening chat text.

## Reflective Failure Feedback

When the selected local model bridge cannot connect, NEX converts raw local transport errors into bounded feedback.

Example:

```text
WinError 10061 -> Ollama/local model server is not accepting the connection.
```

NEX should then recommend the next bounded local test instead of showing only a raw exception.

## Boundary

NEX remains recommendation-only.

It does not:

- execute model output
- mutate repo files from model output
- grant authority
- hide blocker evidence
- bypass gates

This is a UI reflection polish layer, not a production validation or safety proof.
