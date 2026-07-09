
# NEXUS Wound Compression Engine

v0.9.8 adds a read-only wound compression layer for NexusGate.

The engine reduces failed validation state into one compact active-wound packet instead of letting closers chase stdout tails, individual README markers, or stale assumptions.

## Core Rule

```text
stdout = smoke only
files = evidence
tail = never truth
passed gates = certificates
active wound = one repair target
```

## Evidence Inputs

| Surface | Role |
|---|---|
| `reports/nexus_bounded_runtime_report_latest.json` | Bounded test truth packet |
| `reports/nexus_compile_report_latest.json` | Compiler truth packet |
| `reports/nexus_toolbelt_latest.json` | Toolbelt context packet |
| `git status --short` | Local change surface |

## Output Packets

```text
reports/nexus_wound_compression_latest.json
state/loops/nexus_wound_compression_latest.json
```

## Operator Commands

```powershell
.\scripts\nexus.ps1 wound-compress -Tag "<failed gate>"
```

```bash
bash scripts/nexus.sh wound-compress "<failed gate>"
```

## Boundary

Wound Compression is a read-only evidence reducer. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.
