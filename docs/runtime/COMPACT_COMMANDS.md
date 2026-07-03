# Compact Runtime Commands

NEXUS GATE now exposes one compact PowerShell surface and one compact Bash surface.

## PowerShell

```powershell
.\scripts\nexus.ps1 rehydrate
.\scripts\nexus.ps1 compile
.\scripts\nexus.ps1 status
.\scripts\nexus.ps1 loop -Cycles 5
.\scripts\nexus.ps1 promote
```

## Bash

```bash
bash scripts/nexus.sh rehydrate
bash scripts/nexus.sh compile
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
```

## Windows Bash Note

If Windows exposes `bash` through WSL but no distribution is installed, local Bash validation is skipped. The Bash files remain in the repository and can be validated in Git Bash, WSL with a distro, Linux, macOS, or Ubuntu CI.
