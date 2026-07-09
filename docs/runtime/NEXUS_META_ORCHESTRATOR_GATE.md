# NEXUS Meta-Orchestrator Gate v1.1.3

The Meta-Orchestrator Gate turns the current loop stack into one bounded recommendation surface.

It reads Toolbelt, Preflight, Wound Compression, Phi Gate Supervisor, compiler, and git-scope evidence, then emits a compact report for Codex, chat handoff, and the Electron HUD.

```powershell
.\scripts\nexus.ps1 meta-orchestrator -Tag "<intent>"
```

```bash
bash scripts/nexus.sh meta-orchestrator "<intent>"
```

## Sequence

```text
toolbelt -> preflight-json -> wound-compress -> phi-gate-compile -> selected-gate
```

## Electron HUD

Electron may read `reports/nexus_meta_orchestrator_gate_latest.json`.

The HUD shows a compact Meta-Orchestrator station and opens an expanded panel set when the operator requests more detail. Panels are reflection surfaces only.

## Boundary

The Meta-Orchestrator Gate recommends. It does not execute arbitrary shell commands, mutate the repo, stage files, commit, push, call external APIs, read secrets, self-authorize, or grant UI authority.

Human intent remains the authority surface.

## Claim Boundary

Meta-Orchestrator Gate compilation is local development evidence only. It does not prove correctness, safety, security, production readiness, model understanding, or autonomous authority.
