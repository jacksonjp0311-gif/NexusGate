# NexusCell Entrypoint

## Python

```powershell
python -m nexus_gate.nexus_cell.cli doctor --root .
python -m nexus_gate.nexus_cell.cli run --root . --runner mock --payload .\NexusCell\examples\hello.ps1
python -m nexus_gate.nexus_cell.cli ledger --root .
python -m nexus_gate.nexus_cell.cli policy --root .
```

## NexusGate CLI

```powershell
python -m nexus_gate.cli cell doctor --root .
python -m nexus_gate.cli cell run --root . --runner mock --payload .\NexusCell\examples\hello.ps1
```

## PowerShell

```powershell
.\scripts\nexus.ps1 cell
.\scripts\nexus.ps1 cell-doctor
.\scripts\nexus.ps1 cell-run
.\scripts\nexus.ps1 cell-ledger
.\scripts\nexus.ps1 cell-policy
```
