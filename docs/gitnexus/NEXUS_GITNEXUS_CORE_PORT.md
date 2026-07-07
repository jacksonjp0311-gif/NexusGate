# NexusGate GITNEXUS Core Port v0.1.0

This ports the useful codegraph idea into NexusGate's own Python/Electron process.

This is not a wound-close script.
This does not touch Mode Selection Green HUD links/assets.

v0.1.0:
- scans repo files
- extracts Python classes/functions/imports
- extracts JS/TS symbols/imports conservatively
- extracts PowerShell functions
- builds dependency edges
- reads git working-tree changes
- writes evidence report/state/ledger
- mounts a GITNEXUS HUD launcher into Electron

GITNEXUS output is evidence, not authority.
