# Compact Runtime Commands

NEXUS GATE exposes one compact PowerShell surface and one compact Bash surface.

## PowerShell

```powershell
.\scripts\nexus.ps1 rehydrate
.\scripts\nexus.ps1 compile
.\scripts\nexus.ps1 strict
.\scripts\nexus.ps1 status
.\scripts\nexus.ps1 loop -Cycles 5
.\scripts\nexus.ps1 promote
```

## Bash

```bash
bash scripts/nexus.sh rehydrate
bash scripts/nexus.sh compile
bash scripts/nexus.sh strict
bash scripts/nexus.sh status
bash scripts/nexus.sh loop --cycles 5
bash scripts/nexus.sh promote
```

## Law

```text
One command surface.
Same gates.
Less syntax.
No compile pass, no promotion.
No rehydration without failure/update visibility.
No shadow failure without wound route.
```

Boundary: compact commands improve usability only. Not a safety proof.
