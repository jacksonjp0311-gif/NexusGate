# NEXUS Preflight Optimizer

v0.9.9 adds a read-only preflight layer before future generated closers run.

## Purpose

The Preflight Optimizer checks the next mutation surface before code is changed. It exists because v0.9.7/v0.9.8 proved that repeated failures were often not core architecture wounds; they were preflight misses: command-surface drift, packet-contract drift, README exact-contract drift, bounded-report shape assumptions, and ignored-file staging risk.

## Truth Rule

```text
stdout = smoke only
files = evidence
tail = never truth
passed gates = certificates
active wound = one repair target
preflight = predict likely closure wounds before mutation
```

## Commands

```powershell
.\scripts\nexus.ps1 preflight -Tag "<intent>"
.\scripts\nexus.ps1 preflight-json -Tag "<intent>"
```

```bash
bash scripts/nexus.sh preflight "<intent>"
bash scripts/nexus.sh preflight-json "<intent>"
```

## Gates

- command_surface_parity
- readme_current_line
- packet_contracts
- bounded_report_shape
- ignored_stage_risk

## Boundary

Preflight Optimizer is read-only. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.
