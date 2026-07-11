# NEXUS Predictive Gate Timing

Predictive Gate Timing / Runtime Pressure Model converts prior local gate timing into bounded runtime expectations.

It reads:

- `reports/human_surface/*`

It writes:

- `reports/nexus_predictive_gate_timing_latest.json`
- `state/loops/nexus_predictive_gate_timing_latest.json`

The loop estimates:

- latest lane duration
- median duration
- p90 duration
- drift ratio
- timeout/failure pressure
- recommended next timeout budget
- recommended next efficient command

Core rule:

```text
duration history -> baseline -> drift -> anomaly -> bounded recommendation
```

This is a recommendation-only loop. It may help Codex and chat sessions avoid waste by preferring targeted gates before full `evolve`. It may not hide failures, bypass gates, extend timeouts autonomously, mutate the repo, or replace human authorization.

Run:

```powershell
.\scripts\nexus.ps1 predictive-timing
```

or:

```bash
bash scripts/nexus.sh predictive-timing
```

Claim boundary: local development evidence only. It does not prove future duration, correctness, safety, security, production readiness, or autonomous authority.
