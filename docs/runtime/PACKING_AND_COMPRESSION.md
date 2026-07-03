# Packing and Compression

NEXUS GATE now includes a pack compiler.

## PowerShell

```powershell
.\scripts\nexus.ps1 pack
```

or:

```powershell
.\scripts\nexus_pack.ps1
```

## Bash

```bash
bash scripts/nexus.sh pack
```

or:

```bash
bash scripts/nexus_pack.sh
```

## What packing does

```text
Python compile
unit tests
NEXUS compiler
source file scan
SHA-256 file manifest
compressed tar.gz source bundle
pack manifest
```

Outputs:

```text
dist/nexus_gate_source_bundle_latest.tar.gz
dist/nexus_gate_pack_manifest_latest.json
```

## Compression Law

```text
No growing code surface without a pack report.
No release without compile, tests, compiler, and pack manifest.
No new feature unless it advances the governed transfer boundary.
```

Boundary: a pack report is local engineering evidence only.
