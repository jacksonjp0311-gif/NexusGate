# NEXUS Desktop Entry Portal

The Desktop entry portal creates two local Desktop entry points:

`	ext
NEXUS Gate.lnk
NEXUS Gate Console.cmd
`

The primary option is:

`	ext
1. Open NexusGate
`

Open NexusGate runs the Electron preflight lane and then opens the presentation-only Electron UI from:

`	ext
electron/package.json
npm start
`

Launcher script:

`	ext
scripts/desktop/open_nexus_gate_console.ps1
`

Icon asset:

`	ext
assets/icons/nexus_gate.ico
`

Secondary governed lanes:

`	ext
status
tui
nn-health
ask
open repo folder
`

Boundary:

- The launcher does not grant model authority.
- Electron remains a presentation/operator surface.
- The launcher does not execute model output as shell.
- The launcher does not mutate files from model output.
- The launcher does not bypass NEXUS gates.
- Human authorization remains required for durable mutation.

## Electron Selector Switch

The Electron entry portal includes a local reasoning selector:

```text
FAST / Phi-3
BALANCED / Phi-3
DEEP / Mistral
HANDOFF / ChatGPT-Codex
```

The selector is UI planning context only. It does not call models or grant authority.
