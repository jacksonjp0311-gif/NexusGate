# NEXUS GATE v0.4.0 Codex Orchestration Protocol

Codex should not enter an empty repo. Codex should enter a repo that teaches it.

## Required Operating Order

1. Rehydrate before patching.
2. Read `README.md`, `AGENTS.md`, `reports/nexus_reflective_loop_report_latest.json`, `state/nexus_lineage_manifest_latest.json`, and `state/interface_adapter_contract_index.v0.3.7.json`.
3. Inspect domain intelligence reports before creating new claims.
4. Use bounded patches.
5. Run tests.
6. Run `.\scripts\nexus.ps1 domain`.
7. Run `.\scripts\nexus.ps1 reflect`.
8. Run `.\scripts\nexus.ps1 evolve`.
9. Commit only after gates pass.
10. Report what changed, what passed, what failed, and what remains blocked.

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
```
