# NEXUS GITNEXUS Upstream Bridge v0.5.0

## Diagnosis

The v0.4.x standalone HUD was a visual clone. It was not the real GitNexus Web UI.
The real GitNexus web stack uses React, Sigma, Graphology, ForceAtlas2,
Graphology noverlap, and the GitNexus local HTTP server.

## Correct integration

NexusGate should not keep reimplementing the full GitNexus renderer. The stable
integration is:

- native NexusGate mini dock
- full HUD iframe to real GitNexus Web UI
- GitNexus local bridge server from `gitnexus serve`
- no runtime hijacking of NexusGate
- no fake graph engine

## Operator commands

From the NexusGate repo root:

```powershell
.\scripts\nexus_gitnexus_upstream.ps1 analyze
.\scripts\nexus_gitnexus_upstream.ps1 serve
```

Keep the serve terminal open. Then open NexusGate UI and click:

```text
GITNEXUS -> OPEN
```

## Boundary

GITNEXUS remains evidence-only. It does not change NexusCell policy, execute
shell commands from model output, or grant autonomous mutation authority.