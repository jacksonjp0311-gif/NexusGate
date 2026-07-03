# Validation Surface

## Required local gate

```powershell
python -m nexus_gate.compiler --root . --json
```

## Required tests

```powershell
python -m compileall nexus_gate tests
python -m unittest discover -s tests
```

## PowerShell surface

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_once.ps1
```

## Bash surface

```bash
bash scripts/nexus_once.sh
```

Boundary: validation surface is a local development gate only.
