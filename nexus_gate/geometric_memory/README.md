# NEXUS Geometric Memory Runtime

## RCC Nexus Echo Location

Package:
`nexus_gate/geometric_memory/`

Purpose:
Read-only runtime packet layer for the Geometric Memory Router.

Validation:
```powershell
python -m nexus_gate.geometric_memory.router --root . --intent "speed test" --json
python -m unittest discover -s tests -p test_geometric_memory_router_runtime_v083.py -v
```

Boundary:
This package emits geometry packets. It does not repair files, call models, train Mistral, mutate weights, or authorize repo mutation.


Cleanup:
```powershell
python -m nexus_gate.geometric_memory.cleanup --root . --json
.\scripts\nexus.ps1 geo-clean
```

Cleanup removes generated/untracked geometry packets and timestamped report residue. It skips tracked files by default.

