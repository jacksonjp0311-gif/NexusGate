# Nexus Meta Loop Registry

Version: v0.9.0

Purpose: let generated scripts call repository-owned local loops by name instead of duplicating full rehydration, validation, failure intelligence, receipt, cleanup, and promotion logic.

## Core Pattern

```text
AI generates trigger
-> local loop registry resolves loop name
-> local runner executes ordered stages
-> verifier gates decide continuation
-> receipt/failure packet is written
-> human reviews compact intelligence output
```

## Canonical Loops

```text
rhp-core
  Deep repository-origin rehydration.

script-evolution
  Plan, rehydrate, validate, receipt, clean, status, and stop before unauthorized commit/push.

reflective-validation
  Run compiler/test gates and compress failure intelligence.

failure-intelligence
  Bind the next patch to the latest wound and update visibility surfaces.

validate-promote
  Run verification gates and stop before durable mutation unless human-authorized.
```

## Trigger Contract

Generated scripts should call:

```powershell
python -m nexus_gate.loops.runner --root . --loop rhp-core --intent "<intent>" 
python -m nexus_gate.loops.runner --root . --loop script-evolution --intent "<intent>" 
python -m nexus_gate.loops.runner --root . --loop validate-promote --intent "<intent>" --execute --human-authorized 
```

PowerShell surface:

```powershell
.\scripts\nexus.ps1 loops
.\scripts\nexus.ps1 meta-loop -Loop rhp-core -Tag "inspect repo"
.\scripts\nexus.ps1 meta-loop -Loop validate-promote -Tag "verify patch" -Execute -HumanAuthorized
```

Bash surface:

```bash
bash scripts/nexus.sh loops
bash scripts/nexus.sh meta-loop rhp-core "inspect repo"
```

## Boundary

The loop runner may read files, emit digests, plan stages, run named allowlisted local commands when explicitly authorized, and write compact packets.

The loop runner may not self-authorize durable mutation, commit, push, promote memory, access secrets, enable network, install services, execute arbitrary shell strings, or claim correctness/security/safety proof.

## Outputs

```text
reports/nexus_loop_packet_latest.json
state/loops/loop_state_latest.json
```