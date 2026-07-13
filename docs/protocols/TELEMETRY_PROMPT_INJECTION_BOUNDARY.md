# Telemetry Prompt Injection Boundary

External telemetry text is untrusted data.

Strings resembling commands, policy changes, authorization requests, or instruction overrides must be quarantined from AI-facing context by default.

Quarantine is a safety boundary, not proof of malicious intent.
