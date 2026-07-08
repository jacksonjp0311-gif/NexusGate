# ChatGPT Script Doctrine

## Required Read Before Coding

This file must be read before ChatGPT, Codex, an agent, or any generated All-One script modifies this repository.

```json
{
  "doctrine": "chatgpt_script_gate_process",
  "status": "required_before_coding",
  "repo": "NexusGate",
  "authority": "human_authorized_only",
  "core_rule": "gates_are_certificates_do_not_backtrack_without_changed_inputs"
}
```

## Why This Exists

NEXUS GATE is built by compact script closures, not loose patches. The v0.9.1 seal showed the correct process:

1. Rehydrate from the repository, not chat memory.
2. Read the README, docs index, entrypoints, core algorithms, update chart, failure chart, compiler report, and target surface.
3. Name the exact organ/version being changed.
4. Generate one bounded All-One script.
5. Run gates in order.
6. Treat every passed gate as a certificate.
7. If a later gate fails, resume from the failed gate instead of rerunning green gates.
8. Record the active wound in machine-readable form.
9. Patch the smallest surface that closes the wound.
10. Compile, test, run the Nexus compiler, stage intended files only, then commit/push only with explicit human authorization.

## Gate Semantics

```json
{
  "gate_semantics": {
    "pass": "certificate_for_current_inputs",
    "fail": "active_wound",
    "resume": "start_from_failed_gate",
    "backtrack": "allowed_only_if_a_passed_gate_input_changed",
    "compiler": "final_local_seal",
    "push": "allowed_only_after_green_seal_and_explicit_human_authorization"
  }
}
```

## Standard Script Shape

```text
GATE 01: Show HEAD / origin
GATE 02: RHP origin packet
GATE 03: Apply minimal patch
GATE 04: Quarantine known prior-wound residue
GATE 05: Compile changed Python and tests
GATE 06: Run targeted wound tests
GATE 07: Emit required packets/reports
GATE 08: Run bounded full test suite or certified resume gate
GATE 09: Run Nexus compiler
GATE 10: Stage intended files only
GATE 11: Commit only after green seal
GATE 12: Push only when the human passed -Push
```

## Machine State Packet

Every generated closer should print or write a compact state packet:

```json
{
  "repo": "NexusGate",
  "target": "version_or_organ",
  "state": "patched_not_sealed|sealed|failed",
  "last_good_gate": "gate_id",
  "active_wound": "exact_failed_gate_or_test",
  "resume_from": "gate_id",
  "do_not_rerun": ["certified_green_gates"],
  "stage_policy": "intended_files_only",
  "push_policy": "human_authorized_only"
}
```

## Coding Preferences

- Prefer one downloadable PowerShell script that launches a Python controller.
- Keep PowerShell as the launcher, not the complex logic layer.
- Use Python for patching, gate orchestration, JSON reports, and bounded test execution.
- Avoid brittle regex where anchored replacement or direct file writing is safer.
- Capture stdout/stderr into compact logs.
- Fail only on exit codes or explicit contract violations, not harmless stderr progress.
- Do not dump huge logs into chat.
- Preserve tests that encode old lineage markers unless the test itself is intentionally evolved.
- Do not stage unrelated runtime residue, report churn, ledgers, memory files, or backup debris.
- Use `git reset` before staging intended files when stale staging is possible.
- Always show or record staged files before commit.

## Wound Lessons From v0.9.1

```text
021H: PowerShell quoting wounds can block before repo mutation.
021I: command runner argument naming can drop git subcommands.
021J: unittest module invocation can fail when tests/ is not an import package.
021K: test progress on stderr is not necessarily failure.
021L: PowerShell typed objects can create false gate failures.
021M: full-suite monoliths can stall; bounded per-file runners isolate wounds.
021N: report-object logic belongs in Python, not PowerShell.
021O: bounded suite identified the real README freshness wound.
021P: freshness healed; bounded suite surfaced README rehydration wound.
021Q: bounded suite passed; compiler became the final seal.
021R/021S/021T: resume from the exact compiler gate; do not rerun green gates.
```

## Non-Authority Boundary

This doctrine improves repository continuity. It does not grant autonomous authority, production safety proof, security proof, correctness proof, provider authority, memory write authority, shell authority, commit authority, or push authority.
