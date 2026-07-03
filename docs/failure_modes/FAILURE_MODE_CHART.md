# NEXUS GATE Failure Mode Chart

This chart must be visible during rehydration.

## Current Failure Modes

| Failure ID | Layer | Trigger | Severity | Required Response | Rehydration Visibility |
|---|---|---|---|---|---|
| `schema_missing` | route | Packet lacks schema identity. | block | Reject route. | Always show. |
| `authority_unverified` | authority | Action requests mutation without authority scope. | block | Shadow or reject. | Always show. |
| `origin_dehydrated` | RHP | Session state drifted from repository origin. | critical | Rehydrate before mutation. | Always show. |
| `compiler_failed` | compiler | Gated compiler status is fail. | block | No commit, no promotion. | Always show latest report. |
| `unit_test_failed` | tests | Unit tests fail. | block | No checkpoint. Patch smallest surface. | Always show. |
| `mini_readme_missing` | RCC/Nexus | Target folder lacks local orientation. | warning | Repair mini README before patching. | Always show target route. |
| `ledger_unavailable` | evidence | Ledger cannot append. | critical | Block compounding. | Always show. |
| `direct_compiler_call_missing` | scripts | Runtime script does not call compiler directly. | block | Repair script. | Always show. |
| `claim_boundary_missing` | docs/reports | Report lacks non-claim boundary. | warning | Add boundary before public claim. | Always show. |
| `shadow_failure_unrouted` | cold evidence | Shadow run fails without wound/failure route. | block | Convert to failure-mode record. | Always show. |
| `replay_missing` | replay | Re-engagement lacks replay certificate. | block | Block re-engagement. | Always show. |
| `update_chart_stale` | docs/updates | Version changed without update chart entry. | warning | Update chart and ledger. | Always show. |
| `readme_dual_shell_rule_missing` | README/tests | README missing exact dual-shell rule string. | block | Restore exact rule. | Always show. |
| `bash_env_unavailable` | local environment | Windows exposes WSL bash but no distro is installed. | warning | Skip local Bash validation; keep Bash scripts and CI validation. | Always show. |
| `powershell_syntax_too_large` | installer/runtime | Long native PowerShell syntax creates parser fragility. | warning | Prefer compressed payload and compact command surface. | Always show. |
| `packer_output_outside_root` | build/pack | Pack test writes to temp dir outside repo, but packer tries repo-relative path. | block | Use safe display path helper. | Always show. |
| `update_chart_history_dropped` | docs/updates | New chart overwrites old lineage row still required by tests. | block | Restore historical rows; never delete lineage casually. | Always show. |

## Laws

```text
No rehydration without failure chart visibility.
No patch without failure mode classification.
No recovery without ledger update.
No repeated failure without chart update.
No chart update without compiler validation.
No pack report without safe output path handling.
No update chart without preserved lineage rows.
```

Boundary: this chart is a local development control. It does not prove safety, security, correctness, or production readiness.
