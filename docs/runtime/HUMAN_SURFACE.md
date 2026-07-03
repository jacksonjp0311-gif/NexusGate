# Human-Readable Runtime Surface

The human surface is the preferred PowerShell run path.

## Command

```powershell
.\scripts\nexus.ps1 human
```

## What it runs

```text
Python compile
unit tests
NEXUS compiler
adapter compiler
receptor compiler
bridge compiler
runtime compiler
pack compiler
```

## Output rule

The terminal prints compact status lines only.

Detailed JSON and logs are written to:

```text
reports/human_surface/
reports/nexus_compile_report_latest.json
reports/nexus_adapter_compile_report_latest.json
reports/nexus_receptor_compile_report_latest.json
reports/nexus_bridge_compile_report_latest.json
reports/nexus_runtime_compile_report_latest.json
dist/nexus_gate_pack_manifest_latest.json
```

## Git warning rule

CRLF/LF conversion warnings are filtered from normal operator output. They are not treated as build failures.

Boundary: human surface improves operator clarity only. It does not prove production readiness.
