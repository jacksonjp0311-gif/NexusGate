param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path)
python -m nexus_gate.nexus_cell.cli doctor --root $Root
exit $LASTEXITCODE
