# NEXUS Phi Gate Supervisor v1.1.1

The Phi Gate Supervisor is a failure-boundary microdose lane.

## Flow

```text
run gate
  -> if pass: continue
  -> if fail: compress/detect wound
  -> call local Phi microdose through the Ollama adapter
  -> select only an allowlisted deterministic repair lane
  -> apply repair only when human-authorized
  -> rerun the same gate
  -> continue only after pass
```

## Safe Repair Lanes

```text
loop_registry_card_packet_drift
empty_loop_stages
ignored_report_staged
readme_compactness_regression
preflight_docs_contract_drift = report only
```

## Boundary

Phi advises, diagnoses, and selects an allowlisted repair lane. Nexus verifies. The human authorizes durable mutation. This supervisor does not grant arbitrary shell authority, secret access, external network authority, autonomous git authority, safety proof, security proof, or correctness proof.

## v1.1.2 Compiler Seal

The supervisor now has a contract compiler:

```powershell
.\scripts\nexus.ps1 phi-gate-compile
```

It writes:

```text
reports/nexus_phi_gate_supervisor_report_latest.json
reports/nexus_phi_gate_supervisor_report.v1.1.2.json
```

The compiler checks:

```text
docs and state surfaces exist
PowerShell and Bash expose phi-gate-compile
PowerShell, Bash, and loop registries use --call-model
PowerShell, Bash, and loop registries use --auto-repair
legacy --call-phi and --self-heal flags are absent
authority boundaries remain false for shell/git/network/secrets/autonomous mutation
deterministic allowlisted repairs remain declared
human authorization boundary remains visible
```

Compiler status is local development evidence only. It does not prove correctness, safety, security, production readiness, or autonomous authority.
