# NEXUS Predictive Evolve

Predictive Evolve is a dry-run planner for expensive validation. It does not execute the plan. It reads predictive timing, inspects changed-file scope, recommends the cheapest useful next gate, and still requires full `evolve` before commit.

Core loop:

```text
predictive timing -> scope classification -> gate selection -> dry-run plan -> final evolve seal required
```

It reads:

- `reports/human_surface/*`
- `git status --porcelain`
- `reports/nexus_predictive_gate_timing_latest.json`

It writes:

- `reports/nexus_predictive_evolve_plan_latest.json`
- `state/loops/nexus_predictive_evolve_plan_latest.json`

Dry-run rules:

- It may recommend targeted docs, Python, Electron, or timing gates.
- It may expose runtime pressure and timeout budget recommendations.
- It may not mutate the repo.
- It may not execute arbitrary shell commands.
- It may not write git state.
- It may not skip the final full evolve seal before commit.
- It may pair with `.\scripts\nexus.ps1 certificate-resume` after a failed gate to inspect passed-gate certificates and recommend the active resume point.

Run:

```powershell
.\scripts\nexus.ps1 predictive-evolve
```

or:

```bash
bash scripts/nexus.sh predictive-evolve
```

Claim boundary: local dry-run planning evidence only. It does not prove correctness, safety, security, production readiness, future runtime duration, or autonomous authority.
