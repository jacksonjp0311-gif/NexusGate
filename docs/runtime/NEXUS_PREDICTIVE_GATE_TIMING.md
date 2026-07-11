# NEXUS Predictive Gate Timing

Predictive Gate Timing / Runtime Pressure Model converts prior local gate timing into bounded runtime expectations.

It reads:

- `reports/human_surface/*`
- `git status --porcelain`

It writes:

- `reports/nexus_predictive_gate_timing_latest.json`
- `state/loops/nexus_predictive_gate_timing_latest.json`
- `ledger/runtime_gate_timings.jsonl`

The loop estimates:

- latest lane duration
- median duration
- p90 duration
- drift ratio
- timeout/failure pressure
- recommended next timeout budget
- recommended next efficient command
- changed-file scope
- cheapest valid next gate recommendation

Core rule:

```text
duration history -> baseline -> drift -> anomaly -> bounded recommendation
```

Adaptive timeout policy:

```text
timeout = max(min_timeout, min(max_timeout, p90 * 1.5))
```

Gate selection policy:

```text
docs-only -> docs/readme tests first
electron-only -> electron smoke first
python-only -> targeted unit tests first
high runtime pressure -> predictive timing + bounded tests first
final commit path -> full evolve remains required
```

This is a recommendation-only loop. It may help Codex and chat sessions avoid waste by preferring targeted gates before full `evolve`. It may not hide failures, bypass gates, extend timeouts autonomously, mutate the repo, or replace human authorization.

Predictive Evolve consumes this timing surface as a dry-run planner:

```text
predictive timing -> scope classification -> gate selection -> dry-run plan -> final evolve seal required
```

Run `.\scripts\nexus.ps1 predictive-evolve` when you want a compact next-gate plan without executing the plan.

Run:

```powershell
.\scripts\nexus.ps1 predictive-timing
```

or:

```bash
bash scripts/nexus.sh predictive-timing
```

Claim boundary: local development evidence only. It does not prove future duration, correctness, safety, security, production readiness, or autonomous authority.
