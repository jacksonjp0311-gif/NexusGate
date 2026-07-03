# Adapter Registry

The adapter registry is the first concrete NEXUS GATE bridge surface.

## Law

```text
No adapter, no bridge.
No manifest, no registration.
No normalized StatePacket, no route.
No receptor export, no transfer target.
```

## Current Adapter

| Adapter | Purpose | Status |
|---|---|---|
| `local.demo` | Local demo adapter proving event -> StatePacket -> router path. | registered |

## Required Adapter Contract

Each adapter must provide:

```text
AdapterManifest
detect_capabilities()
normalize_event(raw_event) -> StatePacket
export_receptors()
supports_shadow()
```

Boundary: adapter registration is local compatibility evidence only. It does not prove production interoperability.
