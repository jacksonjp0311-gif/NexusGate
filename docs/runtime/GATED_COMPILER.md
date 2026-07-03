# NEXUS GATE Gated Compiler

The first installer could freeze if its PowerShell helper launched plain `python` without the module arguments.

This rescue patch installs the direct compiler command:

```powershell
python -m nexus_gate.compiler --root . --json
```

The compiler is a development gate:

```text
repository state
  -> required paths
  -> runtime law check
  -> JSON parse
  -> forbidden bypass scan
  -> Python compile
  -> route contracts
  -> unit tests
  -> ledger append
  -> report
  -> pass | fail
```

Runtime law:

```text
No compile pass, no promotion.
No schema pass, no route.
No authority pass, no mutation.
No tests pass, no checkpoint.
No ledger entry, no compounding.
```