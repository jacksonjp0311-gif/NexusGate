# NEXUS Predictive Memory Orchestrator

Predictive Memory Orchestrator fuses Cortex memory evidence with predictive gate planning.

Core loop:

```text
Cortex gate -> vector benchmark -> card memory -> predictive evolve -> recommendation -> trend ledger
```

It reads:

- `reports/nexus_cortex_gate_latest.json`
- `reports/nexus_cortex_sync_report_latest.json`
- `reports/nexus_cortex_vector_benchmark_latest.json`
- `state/algorithms/nexus_algorithm_cards_latest.json`
- `state/discoveries/nexus_discovery_cards_latest.json`
- `reports/nexus_predictive_evolve_plan_latest.json`
- `git status --porcelain`

It writes:

- `reports/nexus_predictive_memory_orchestrator_latest.json`
- `state/loops/nexus_predictive_memory_orchestrator_latest.json`
- `ledger/cortex_benchmark_trends.jsonl`

Rules:

- It may recommend a Cortex refresh, vector migration, targeted gate, or final evolve seal.
- It may record benchmark trend rows for Cortex memory health.
- It may not execute the recommended plan.
- It may not mutate the repo.
- It may not promote memory autonomously.
- It may not skip final `evolve` before commit.

Run:

```powershell
.\scripts\nexus.ps1 predictive-memory
```

or:

```bash
bash scripts/nexus.sh predictive-memory
```

Claim boundary: local planning evidence only. It does not prove retrieval correctness, model understanding, safety, security, production readiness, or autonomous authority.
