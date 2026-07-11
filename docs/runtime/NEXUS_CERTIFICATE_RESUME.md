# NEXUS Certificate Resume

Certificate Resume v0.1 records passed-gate evidence from the latest human-surface run.

Core loop:

```text
latest human_surface run -> gate status -> evidence hash -> input fingerprint -> resume recommendation -> final evolve seal required
```

It writes:

- `reports/nexus_certificate_resume_report_latest.json`
- `state/loops/nexus_certificate_resume_latest.json`

It may:

- hash passed gate logs
- record local gate certificates
- identify the first failed or timed-out gate
- recommend the active resume point

It may not:

- claim a pass from certificates alone
- skip final full `evolve` before commit
- mutate the repo
- write git state
- self-authorize
- hide failures

Run:

```powershell
.\scripts\nexus.ps1 certificate-resume
```

Claim boundary: local development evidence only. Certificates are useful resume evidence, not proof of correctness, safety, security, production readiness, or authority.
