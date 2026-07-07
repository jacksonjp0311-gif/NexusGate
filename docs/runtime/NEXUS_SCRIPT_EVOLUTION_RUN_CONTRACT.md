# Nexus Script Evolution Run Contract

Version: v0.1.2

This contract teaches humans and rehydrating AI systems how generated scripts should report failures, tracebacks, verification, and GitHub push results without dumping huge assertion strings into chat.

## Failure Compiler

Every All-One script should compile failures into a compact report instead of printing whole logs.

Required fields:

```text
wound_id
stage
exit_code
log_path
log_line_count
failed_tests
traceback_heads
assertion_summary
doctor_summary
next_close_target
stability_lock
```

Default outputs:

```text
reports/nexus_compiled_failure_latest.json
reports/nexus_compiled_failure_latest.md
```

Console output should show the compact failure report and the log path. It should not dump large README bodies, large JSON payloads, full assertion strings, or full traceback logs.

## Traceback Compression Rule

Extract only important lines and nearby context:

```text
FAIL:
ERROR:
Traceback
AssertionError
SyntaxError
ParserError
Exception
FAILED
stage :
code  :
```

Long lines must be truncated. Console output must be capped.

## End Summary Contract

Every successful script should finish with:

```text
WHAT WAS DONE
VERIFIER
STABILITY LOCK
```

The verifier names every gate that passed. The stability lock includes branch, commit, push state, workspace status, residue policy, and whether generated files were cleaned.

## GitHub Push Compression

If a script pushes to GitHub, it must compress the push into:

```text
branch
commit
message
changed_files
push_result
post_push_status
stability_lock
```

Do not paste raw GitHub diffs unless the human asks.
