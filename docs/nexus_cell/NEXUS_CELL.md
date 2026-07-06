# NexusCell

NexusCell is the execution containment organ of NexusGate.

It extracts the agent-sandbox lifecycle intelligence of CubeSandbox,
translates it into Python-native NexusGate law,
and evolves the sandbox into a governed execution system:

authority-gated,
boundary-sealed,
receipt-emitting,
ledger-backed,
interconnect-visible,
human-authorized.

```text
A sandbox contains code.
NexusCell governs execution.
```

## Portable v0.1 Commands

```powershell
python -m nexus_gate.nexus_cell.cli doctor --root .
python -m nexus_gate.nexus_cell.cli run --root . --runner mock --payload .\NexusCell\examples\hello.ps1
python -m nexus_gate.nexus_cell.cli ledger --root .
python -m nexus_gate.nexus_cell.cli policy --root .
```

## Boundary

```text
NexusCell is local development execution-governance infrastructure.

It is not a production security proof.
It is not a perfect sandbox.
It is not malware-proof.
It is not AGI.
It is not autonomous authority.
It is not a correctness proof.
It is not full rollback until Return Seal backend exists.
It does not replace human authorization.
```
