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
| `statepacket_to_dict_missing` | bridge/session | Bridge runner assumed StatePacket had to_dict. | block | Use safe model/dataclass serialization helper. | Always show. |
| `compact_marker_gate_dropped` | compact scripts | Compact rehydration script dropped literal FAILURE_MODE_CHART marker required by tests. | block | Restore explicit failure chart path. | Always show. |

## Laws

```text
No rehydration without failure chart visibility.
No patch without failure mode classification.
No recovery without ledger update.
No repeated failure without chart update.
No chart update without compiler validation.
No pack report without safe output path handling.
No update chart without preserved lineage rows.
No bridge report without safe packet serialization.
```

Boundary: this chart is a local development control. It does not prove safety, security, correctness, or production readiness.

- compiler_marker_hidden_by_wrapper: human wrapper hid literal compiler marker still required by compatibility tests.


- feedback_missing_compiled_reports: feedback cannot infer health without current compiler/runtime reports.
- interconnect_graph_missing_edges: interconnect graph failed to prove governed transfer edges.
- compaction_manifest_missing: evidence pressure cannot be governed without a compaction manifest.


- bash_failure_chart_marker_missing: Bash compact surface dropped FAILURE_MODE_CHART marker.
- bash_strict_mode_missing: Bash compact surface dropped strict command marker.
- crlf_filter_literal_missing: human surface dropped CRLF/LF filter literal markers.
- self_healing_without_apply_gate: repair recommendation lacks dry-run/apply-gate boundary.


- ai_feedback_context_missing: future AI cannot rehydrate feedback state without state/ai_feedback_context_latest.json.
- feedback_log_missing: feedback loop lacks append-only Markdown handoff surface.
- ps_feedback_summary_missing: PowerShell output does not expose health, pressure, dominant source, next action, context path, and log path.


- forms_ui_patch_operator_error: Windows Forms patch mutation failed before install; use terminal TUI shell instead.
- tui_surface_missing: operator lacks terminal dropdown menu, chat prompt, buffer bar, colored output, AI handoff, and bounded feedback write commands.
- tui_ungated_mutation: TUI attempts repo mutation outside feedback log, operation packet, or governed NEXUS lanes.

- ai_agent_interconnect_unrouted: AI/Codex handoff process lacks governed feedback-context, operator-packet, TUI export, or return-to-operator edge.
- ai_agent_self_authorization: AI/Codex process attempts to treat handoff context as authority instead of recommendation evidence.
- domain_route_without_profile: bio, chem, coding, neural, or CLI data is routed without a declared domain interconnection profile.
- domain_route_claim_inflation: domain routing is treated as scientific validity, code correctness, model correctness, safety, or production readiness.
- tui_graph_mutation_attempt: TUI graph/interconnect view attempts to mutate graph state instead of reading compiled evidence.
- graph_visibility_claim_inflation: graph visibility is treated as proof of correctness, safety, production readiness, scientific validity, model validity, or autonomous authority.
- snapshot_bridge_claim_inflation: TUI snapshot HTML is treated as proof, authority, validation, or runtime ownership instead of read-only evidence orientation.
- tui_surface_state_claim_inflation: TUI surface JSON is treated as proof, authority, validation, shell execution permission, or runtime ownership.
- snapshot_surface_pair_drift: TUI snapshot HTML and surface JSON diverge because they are not refreshed by the same operator action.
- electron_contract_drift: Electron/dashboard plan gains read surfaces or commands outside the tested contract.
- electron_shell_authority_leak: Electron scaffold exposes Node integration, arbitrary shell execution, graph mutation, secret access, or bypasses NEXUS lanes.
- electron_preflight_missing: Electron scaffold exists without a compiled preflight report in the normal evolve evidence chain.


## v0.8.3 Geometric Router Failure Modes

- `readme_anchor_drift`: README/tests; new docs patch removes required compatibility anchor; block; restore old anchor plus new line and rerun readme tests.
- `untracked_cleanup_git_restore_pathspec`: scripts/cleanup; git restore is used on generated untracked files; warning; use Remove-Item for untracked residue and git restore only tracked paths.
- `runpy_eager_package_import`: Python/package; package __init__ imports module also executed with python -m; warning; make __init__ passive/lazy and run python -W error smoke.
- `lazy_import_readback_false_positive`: tests/readback; guard flags lazy import text as eager import; warning; test exact boundary or use importlib lazy access.
- `readme_line_budget_boundary`: README/tests; README hits exact forbidden line-count boundary; block; compact blank lines while preserving required markers.
- `powershell_child_command_expansion`: PowerShell/scripts; expandable child command removes $null variable; warning; avoid assignment or escape child command text.
- `tracked_report_cleanup_hazard`: cleanup/evidence; cleanup deletes tracked report evidence; block; restore tracked evidence before patch and cleanup only untracked residue.
- `powershell_backtick_string_parse_wound`: PowerShell/scripts; backtick escaped closing quote in dynamic string; block; avoid backtick-heavy string construction.


## v0.8.4 NexusCell Failure Modes

- `stale_manifest_version_pin`: NexusCell/tests; exact manifest version was frozen while manifest advanced within v0.8.4 lineage; block; test invariant lineage and accepted status progression.
- `stale_planner_manifest_version_pin`: NexusCell/planner tests; planner test pinned v0.8.4C while compiler visibility advanced to v0.8.4D; block; test planner invariants instead of exact version.
- `compiler_visibility_not_authority`: NexusCell/compiler; compiler visibility is mistaken for execution authority; critical; restore boundary that compiler visibility is not backend enablement.
- `planner_visibility_not_backend_enablement`: NexusCell/planner; read-only planning is mistaken for sandbox execution; critical; restore no-execution/no-backend/no-rollback boundary.
- `doctor_trap_without_self_authority`: Doctor/repair loop; Doctor trap is expected to mutate source automatically; warning; Doctor classifies/recommends and human authorizes patch.
- `stale_compiler_visibility_status_set`: NexusCell/compiler tests; accepted status set froze before NexusShell operator progression; block; accept lawful read-only status progression and rerun shell/cell/compiler gates.
- `close_script_partial_status_patch`: scripts/tests; close script patches source gate but misses regression accepted-status set; block; patch tests and rerun shell/cell/compiler gates.

