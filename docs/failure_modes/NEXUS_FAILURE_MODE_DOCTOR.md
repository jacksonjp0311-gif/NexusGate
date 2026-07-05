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


## FM-090 native_command_stderr_noise

```text
who: PowerShell All-One runner
why: native command progress/test output can appear on stderr
what: runner may stop before Doctor can classify
when: captured tests/compiler/npm/shell command
doctor: safe-capture stdout/stderr into a log
retry: rerun bounded validation with compact log tail on nonzero exit
authority: human_selected_retry
```


## FM-100 json_bom_wound

```text
who: JSON artifact writer
why: JSON was written with UTF-8 BOM but loaded as strict utf-8
what: JSONDecodeError blocks preflight/full-suite
when: package/preflight/compiler JSON loading
doctor: rewrite machine JSON with utf-8 no BOM
retry: rerun JSON tests, full suite, and compiler
authority: human_selected_retry
```


## FM-110 ui_contract_cleanup

```text
who: Electron renderer/UI contract
why: selector authority moved to Yellow Relay HUD but old left glyph/telemetry residue remained
what: obsolete Relay Glyph appears or telemetry HUD does not close
when: after portal/HUD rehydration
doctor: inspect index/renderer/styles as one UI contract
retry: remove left glyph, keep Yellow Relay HUD, force hidden CSS, rerun UI tests/full suite/compiler
authority: human_selected_patch
```
