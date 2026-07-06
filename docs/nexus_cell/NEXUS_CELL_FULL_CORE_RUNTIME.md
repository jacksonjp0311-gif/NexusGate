# NexusCell Full Core Runtime

Version: v0.8.8

## Purpose

This layer writes the full NexusCell core surface.

It adds:

```text
policy map
authority gate
shadow receipt builder
controlled internal runner
run packet
compiler visibility
PowerShell lane
Desktop Portal lane
```

## Controlled Lanes

```text
status
compile
tests
cell-plan
cell-context
cell-bridge
```

## Command

```powershell
python -m nexus_gate.nexus_cell.run --root . --lane cell-bridge --intent "inspect docs only" --json
.\scripts\nexus.ps1 cell-run -Tag "cell-bridge"
```

## Boundary

```text
No arbitrary shell execution.
No backend sandbox claim.
No host mount.
No network.
No secrets.
No git mutation.
No rollback claim.
No self-authorization.
```

Controlled lane execution requires both:

```text
--execute
--human-authorized
```

Even then, execution is limited to named internal lanes only.
