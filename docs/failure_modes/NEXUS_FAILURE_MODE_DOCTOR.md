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


## v0.8.3 Geometric Router Wound Ledger

These wounds came from sealing the Geometric Memory Router and preflight cleanup layers. They are preserved so future agents do not repeat the same boundary mistakes.

## FM-120 readme_anchor_drift
```text
who: README geometry patch
why: new release line replaced legacy test anchor
what: readme rehydration test failed because v0.8.1 UI cleanup line disappeared
when: v0.8.3A geometry contract patch
signs: AssertionError missing v0.8.1 UI cleanup line
doctor: preserve compatibility anchors while adding new release markers
retry: patch README with old anchor plus new geometry line, rerun readme tests/full suite/compiler
authority: human_selected_retry
```

## FM-121 untracked_cleanup_git_restore_pathspec
```text
who: All-One cleanup stage
why: script used git restore on generated/untracked files
what: pathspec did not match known git files after all functional gates passed
when: v0.8.3C runtime packet cleanup
signs: git error pathspec did not match any file known to git
doctor: classify tracked vs untracked before cleanup
retry: use Remove-Item for untracked generated packets and git restore only for tracked paths
authority: human_selected_retry
```

## FM-122 runpy_eager_package_import
```text
who: Python package init
why: package __init__ imported router while router was executed with python -m
what: RuntimeWarning about module already present in sys.modules
when: geometric runtime smoke
signs: RuntimeWarning nexus_gate.geometric_memory.router found in sys.modules
doctor: make package init passive/lazy
retry: use importlib lazy attribute access and run python -W error -m router
authority: human_selected_patch
```

## FM-123 lazy_import_readback_false_positive
```text
who: readback guard
why: readback searched for import text anywhere, including lazy function body
what: good lazy import was falsely classified as eager import
when: v0.8.3E warning seal
signs: __init__.py still imports router eagerly despite import inside __getattr__
doctor: make guard test exact failure condition or remove literal trigger with importlib
retry: replace lazy from-import with importlib.import_module
authority: human_selected_retry
```

## FM-124 readme_line_budget_boundary
```text
who: compact README guard
why: README landed exactly on forbidden boundary
what: guard failed because line count was 220 and requirement is less than 220
when: v0.8.3F close
signs: README too long: 220
doctor: compact blank lines without deleting markers
retry: preserve required markers and compact README below 220 lines
authority: human_selected_retry
```

## FM-125 powershell_child_command_expansion
```text
who: PowerShell parse check
why: child command string contained $null and parent expansion removed variable name
what: child PowerShell saw an assignment beginning with equals sign
when: v0.8.3G close
signs: = : The term '=' is not recognized
doctor: avoid expandable strings for child PowerShell assignments
retry: use command without assignment or single-quoted escaped command text
authority: human_selected_retry
```

## FM-126 tracked_report_cleanup_hazard
```text
who: generated cleanup stage
why: cleanup pattern touched tracked timestamped reports and latest report evidence
what: local working tree showed many tracked report deletions/modifications after push
when: after v0.8.3H successful push
signs: git status shows many D reports/nexus_*_20260703*.json and M report/state files
doctor: restore tracked evidence before new durable patch
retry: git restore reports ledger state docs/feedback, then cleanup only untracked residue
authority: human_selected_restore
```

## FM-127 powershell_backtick_string_parse_wound
```text
who: PowerShell failure-mode save script
why: backtick in double-quoted string escaped the closing quote
what: script failed to parse before any repo mutation occurred
when: v0.8.3I failure-mode save attempt
signs: Missing ')' in method call near [regex]::Escape
doctor: avoid backtick-heavy dynamic string construction in PowerShell
retry: use append-only Python patch section or literal marker checks
authority: human_selected_retry
```
