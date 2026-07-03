# NEXUS GATE Gated Compiler

The NEXUS GATE compiler is a development gate.

It does **not** compile Python into machine code.

It compiles the repository state into a promotion decision:

```text
repository state
  -> required paths
  -> manifest laws
  -> JSON parse
  -> bypass scan
  -> Python compile
  -> route contracts
  -> unit tests
  -> ledger append
  -> compile report
  -> pass | fail
```

## Runtime Law

```text
No compile pass, no promotion.
No schema pass, no route.
No authority pass, no mutation.
No tests pass, no checkpoint.
No ledger entry, no compounding.
```

## Run

```powershell
cd C:\Users\jacks\OneDrive\Desktop\nexus-gate
powershell -ExecutionPolicy Bypass -File .\scripts\nexus_compile.ps1
```

Or:

```powershell
python -m nexus_gate.compiler --root . --json
```

## Reports

Compile reports are written to:

```text
reports/nexus_compile_report_latest.json
reports/nexus_compile_report_YYYYMMDD_HHMMSS.json
```

The ledger receives a `nexus_compile` event after each run.