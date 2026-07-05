# NEXUS NN Model Router v0.6.2

NEXUS NN Model Router v0.6.2 is a bounded local intelligence router for the NEXUS GATE repo. It distributes reasoning packets across local model roles and handoff surfaces without granting model authority.

## Boundary

NEXUS remains a governed local intelligence / transfer boundary.

- Models do not get authority.
- Tools do not self-authorize.
- Handoffs are recommendation-only.
- Human remains durable authority.
- No model output may directly execute tools or mutate files.

## Canonical Rules

- No adapter, no bridge.
- No schema, no route.
- No codec, no transfer.
- No authority, no mutation.
- No replay evidence, no memory promotion.
- No evidence ledger, no compounding.
- Distribute intelligence, not authority.
- No model output may directly execute tools or mutate files.

## Local Model Roles

Detected Ollama manifests are read from:

```text
%USERPROFILE%\OneDrive\Desktop\.ollama\models
```

Role assignment:

| Role | Preferred model | Purpose |
| --- | --- | --- |
| FAST | `phi3:mini` or `phi3:latest` | Quick local recommendation voice |
| BALANCED | `phi3:mini` or `phi3:latest` | Balanced local recommendation voice |
| DEEP | `mistral:latest` | Deeper local recommendation voice |
| HANDOFF | no local model required | Writes ChatGPT/Codex handoff packets |

## Router Outputs

The router generates:

```text
reports/nexus_nn_router_report_latest.json
reports/CHATGPT_HANDOFF_LATEST.md
reports/CODEX_HANDOFF_LATEST.md
state/nexus_nn_router_index.v0.6.2.json
```

## Safe Lanes

The script wrapper supports:

```powershell
.\scripts\nexus.ps1 nn -Tag "What should we do next?"
.\scripts\nexus.ps1 nn-health
.\scripts\nexus.ps1 ask -Tag "What should we do next?"
```

These lanes compile recommendations and handoff packets. They do not execute arbitrary shell, mutate repo files from model output, access secrets, or write external APIs.

## Optional Local Ollama Call

By default, the router only detects local model manifests and writes reports/handoffs.

To allow a local loopback Ollama API call, pass an explicit model-call switch:

```powershell
.\scripts\nexus.ps1 nn -Tag "What should we do next?" -CallModel
```

The only allowed endpoint is local loopback:

```text
http://127.0.0.1:11434/api/generate
```

Model responses remain recommendation-only context.

## Intended Architecture

- BB/EGAT prepares a reasoning packet.
- Phi-3 is FAST/BALANCED quick local voice.
- Mistral is DEEP local reasoning voice.
- ChatGPT/Codex receive compressed handoffs.
- NEXUS gates tool/action authority.
- Human authorizes durable mutation.
