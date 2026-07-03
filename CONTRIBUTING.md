# Contributing to NEXUS GATE

NEXUS GATE uses gated, dual-shell development.

## Required Rule

```text
Every new runtime loop must exist in both PowerShell and Bash.
Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.
No compile pass, no promotion.
```

## Local Development Flow

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

Bash:

```bash
bash scripts/nexus_once.sh
```

## Preferred Change Sequence

```text
1. Define the contract.
2. Define the gate.
3. Define the failure mode.
4. Write the test.
5. Implement minimal runtime behavior.
6. Add both shell surfaces if a loop/runtime command is involved.
7. Run the compiler.
8. Inspect the report.
9. Commit only on pass.
```

## Safety Boundary

Do not add code that grants mutation, memory write, filesystem write, tool call, external API call, spending, deletion, or prompt mutation authority unless it is explicitly guarded by an AuthorityContract and tested.