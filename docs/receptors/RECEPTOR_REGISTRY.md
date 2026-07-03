# Receptor Registry

The receptor registry declares valid transfer targets for normalized StatePackets.

## Law

```text
No receptor, no transfer target.
No compatibility decision, no engagement.
No unsupported schema, no receptor route.
No unsupported action, no receptor route.
```

## Current Receptors

| Receptor | Owner Adapter | Purpose | Status |
|---|---|---|---|
| `local.demo.readonly` | `local.demo` | Accepts read-only NEXUS StatePackets. | registered |
| `local.demo.tool_shadow` | `local.demo` | Accepts tool-call packets only with authority; shadows without authority. | registered |

## Required Receptor Contract

Each receptor must provide:

```text
ReceptorManifest
accepted_schema_families
allowed_actions
requires_authority_for_actions
CompatibilityDecision
```

Boundary: receptor registration is local compatibility evidence only. It does not prove production interoperability.
