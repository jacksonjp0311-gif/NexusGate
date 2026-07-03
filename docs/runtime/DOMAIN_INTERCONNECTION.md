# NEXUS GATE v0.2.7 Domain Interconnection

NEXUS GATE now declares domain interconnection profiles for bio, chem, coding, neural, and CLI formatting routes.

## Source Orientation

The profiles are grounded in public interoperability conventions:

- CLI formatting: PowerShell `Write-Host` color parameters and `Write-Progress` progress rendering.
- Bio: NCBI BioProject, BioSample, and SRA metadata organization.
- Chem: IUPAC InChI/InChIKey identifiers and SMILES structure notation.
- Coding: LSP, SARIF, OpenAPI, and JSON Schema.
- Neural: ONNX model graph/operator/model format interoperability.

## Graph Nodes

```text
terminal:cli_format
domain:bio
domain:chem
domain:coding
domain:neural
schema:domain_interop_profile
```

## Route Shape

```text
ai_agent:codex_process
  -> domain:<bio|chem|coding|neural>
  -> schema:domain_interop_profile
  -> bridge:session
  -> reports:local
  -> feedback:engine
  -> ledger:local
```

CLI formatting route:

```text
operator:tui
  -> terminal:cli_format
  -> reports:local
```

## Domain Gates

```text
Domain routing is not domain validation.
No biological claim without source metadata and validation evidence.
No chemical claim without structure identifier and provenance.
No code-tool route without machine-readable contract or diagnostics evidence.
No neural route without model format, runtime boundary, and evidence report.
No raw JSON wall unless requested.
```

## Claim Boundary

These profiles are local interconnection contracts. They do not prove scientific validity, code correctness, model correctness, safety, production readiness, clinical validity, chemical safety, biological truth, or autonomous authority.
