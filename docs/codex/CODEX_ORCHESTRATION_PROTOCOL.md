# NEXUS GATE v0.4.0 Codex Orchestration Protocol

Codex should not enter an empty repo. Codex should enter a repo that teaches it.

## Required Operating Order

1. Rehydrate before patching.
2. Read `README.md`, `AGENTS.md`, `reports/nexus_reflective_loop_report_latest.json`, `state/nexus_lineage_manifest_latest.json`, and `state/interface_adapter_contract_index.v0.3.7.json`.
3. Inspect domain intelligence reports before creating new claims.
4. Use bounded patches.
5. Run tests.
6. Run `.\scripts\nexus.ps1 predictive-timing` before full evolve, pack, broad tests, Electron smoke, or any long-running validation lane.
7. Run `.\scripts\nexus.ps1 predictive-evolve` when you need a dry-run next-gate plan; it may recommend targeted gates, but full evolve remains required before commit.
8. Run `.\scripts\nexus.ps1 domain`.
9. Run `.\scripts\nexus.ps1 reflect`.
10. Run `.\scripts\nexus.ps1 evolve`.
11. Commit only after gates pass.
12. Report what changed, what passed, what failed, and what remains blocked.

## Codex Boundary

Codex may orchestrate repo tasks, edit files inside the user's request, run local validation, and return evidence. Codex cannot self-authorize, bypass gates, access secrets, write external APIs, or promote unsupported claims.

## Required Read Surfaces

```text
README.md
AGENTS.md
docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md
docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md
docs/intelligence/REPO_NATIVE_LEARNING.md
docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md
state/nexus_lineage_manifest_latest.json
state/interface_adapter_contract_index.v0.3.7.json
state/domain_intelligence_index.v0.4.0.json
reports/nexus_reflective_loop_report_latest.json
reports/nexus_domain_intelligence_report_latest.json
reports/nexus_predictive_gate_timing_latest.json
reports/nexus_predictive_evolve_plan_latest.json
state/algorithms/nexus_algorithm_cards_latest.json
state/discoveries/nexus_discovery_cards_latest.json
```

## Predictive Timing Rule

Codex should treat predictive timing as a runtime-pressure preflight. The packet may recommend a cheaper next gate or a bounded timeout. It cannot authorize mutation, hide failures, bypass gates, or replace the final evolve seal.
