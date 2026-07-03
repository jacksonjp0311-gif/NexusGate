# NEXUS GATE v0.2.2b Self-Healing Feedback Layer

This layer imports the proven CMS loop pattern into NEXUS GATE.

```text
feedback finding
  -> typed repair recommendation
  -> dry-run repair plan
  -> human-authorized apply gate
  -> validation stack
  -> evidence report
```

## Command

```powershell
.\scripts\nexus.ps1 heal
```

or inside the full lane:

```powershell
.\scripts\nexus.ps1 evolve
```

## Locks

```text
No self-healing without typed recommendation.
No recommendation may write directly.
No dry-run may write target surfaces.
No apply gate may execute without explicit human authorization.
No repair closure without validation evidence.
No autonomous commit from self-healing recommendation.
```

## Reports

```text
reports/nexus_self_healing_report_latest.json
```

Claim boundary: local development evidence only. This does not prove autonomous safety, correctness, security, or production readiness.
