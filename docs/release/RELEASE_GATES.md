# Release Gates

NEXUS GATE release discipline is gate-first and dual-shell.

## Promotion Requirements

A version may be promoted only when:

```text
compiler status = pass
unit tests = pass
route contracts = pass
runtime laws = present
README rules = present
JSON/schema parse = pass
forbidden bypass scan = pass
PowerShell and Bash script pairs = present
compile/loop/promote scripts call gated compiler = pass
ledger append = pass
latest report exists
git working tree reviewed
```

## Promotion Commands

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_promote.ps1
```

Bash:

```bash
bash scripts/nexus_promote.sh
```

## Non-Claim Lock

A passing compiler report is not a safety proof, security proof, correctness proof, or production validation claim.