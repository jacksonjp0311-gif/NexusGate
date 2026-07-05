# NEXUS Failure Mode Doctor

Version: v0.7.9B

## Compact syntax

```text
FM := id,key,n,who,why,what,when,signs,doctor,retry,authority
```

This syntax is intentionally compressed but readable.

- `who`: surface that failed
- `why`: root cause class
- `what`: visible effect
- `when`: lifecycle moment
- `signs`: scan markers
- `doctor`: read/classify action
- `retry`: bounded retry route
- `authority`: what human authorization is required

## Gateway

```text
8. Failure Modes / Doctor
```

## Doctor actions

```text
1. List ordered failure modes
2. Doctor scan current state
3. Safe clean generated residue
4. Retry validation checks
```

## Troubleshooting loop

```text
scan -> classify -> explain -> safe clean if selected -> retry checks -> report next lawful action
```

## Self-healing boundary

Doctor may read, classify, recommend, safe-clean generated residue, and retry validation checks.

Doctor may not patch durable source, close wounds without evidence, bypass tests, grant authority, mutate memory, or self-authorize.

## Hermes lesson imported

```text
Doctor classifies.
Self-learning preserves validated lessons.
Human authorization unlocks dangerous transitions.
```

NEXUS adopts that split without importing autonomous authority.
