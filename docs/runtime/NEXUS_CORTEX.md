# NEXUS Cortex Integration

Cortex is imported as a root-local subsystem at `Cortex/`. It is a local-first repository assimilation and selective-memory engine for coding agents. In NEXUS GATE it acts as a bounded evidence organ: it can index, retrieve, route, activate sparse repository context, and emit NexusGate-shaped packets, but it cannot authorize mutation or bypass NEXUS gates.

## Current Bootstrap Result

The NEXUS bootstrap uses a repo-local Cortex home at `state/cortex_memory/`, which is intentionally ignored because it contains a large SQLite runtime database. Cortex has indexed the repository, compiled a sparse neural interlink, and emits NexusGate-shaped packets for rehydration.

The bootstrap certificate status is currently `degraded` because the repository changed during/after assimilation and the observed manifest hash drifted. That is a useful safety behavior: Cortex falls back to `read_only` governor mode instead of claiming authority.

## Sync Protocol

Use the NEXUS sync lane whenever the standalone Cortex repo changes:

```powershell
.\scripts\nexus.ps1 sync-cortex -Tag "C:\Users\jacks\OneDrive\Desktop\Cortex"
.\scripts\nexus.ps1 cortex
```

The sync lane copies only local Cortex source/docs/tests/benchmarks into `Cortex/`. It excludes `.git`, `.cortex`, runtime memory, caches, build output, `__pycache__`, and bytecode. It writes `reports/nexus_cortex_sync_report_latest.json`.

Boundary: sync imports source artifacts only. It does not import upstream git history, runtime memory, secrets, external API state, or mutation authority.

## Certificate Refresh

Use the refresh lane after repo changes settle:

```powershell
.\scripts\nexus.ps1 cortex-refresh
.\scripts\nexus.ps1 predictive-memory
```

The refresh lane runs Cortex `index --force`, `telemetry`, `graph --rebuild`, `migrate-vectors`, `verify`, `activate --refresh always`, `doctor`, and `nexus-packet`. It writes `reports/nexus_cortex_refresh_report_latest.json` and refreshes Cortex's repo-local certificate while keeping NEXUS authority read-only and human-bound.

## Vector Storage Upgrade

Cortex upstream commit `8d5e60b` adds compact versioned vector BLOB storage, migration diagnostics, and a vector migration benchmark. NEXUS migrated the local Cortex memory store:

| Vector check | Result |
|---|---:|
| Legacy vectors scanned | 7,919 |
| Migrated vectors | 7,919 |
| Current versioned BLOB vectors | 7,919 |
| Legacy or invalid vectors after migration | 0 |

Run the migration manually if a future sync reports legacy vectors:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate\Cortex"
python -m cortex --home ..\state\cortex_memory migrate-vectors --repo nexus-gate --json
```

## Benchmarks

Latest local benchmark summary:

| Check | Result |
|---|---:|
| Cortex unit tests | 25 passed |
| Thalamus route plan | 0.337 s |
| NEXUS verify | 20.452 s |
| Sparse interlink | 10.063 s |
| NEXUS packet | 3.489 s |
| Activation with auto-refresh | 40.906 s |
| Sparse benchmark | 262 nodes, 280 synapses, 24 fired nodes |
| Thalamus before/after | target rank improved 4 -> 3, top-3 recall 0% -> 100% |
| Vector payload benchmark | 34.71% smaller vector payload |
| Vector query benchmark | 242.630 ms legacy -> 183.011 ms blob in latest local sample |

The self-host lifecycle benchmark did not run from the vendored copy because `self_host_benchmark.py` performs `git clone --no-local` from the active Cortex folder, and the imported `Cortex/` copy intentionally excludes `.git`. Run that benchmark from the original Git-backed Cortex repository when needed.

## High-Value Integration Path

1. Keep `sync-cortex` as the only supported local source import path.
2. Keep the Cortex compiler gate checking database integrity, manifest freshness, vector format, governor mode, and packet shape.
3. Use `cortex-refresh` after meaningful repo changes, then feed Cortex `nexus-packet` output into Meta-Orchestrator as a recommendation source.
4. Add Electron read-only visibility for Cortex status, top activated paths, and governor state.
5. Keep final authority in NEXUS: Cortex may recommend context; NEXUS gates and the human authorize durable mutation.

## Claim Boundary

Cortex integration is local development evidence only. It does not prove correctness, safety, security, production readiness, biological fidelity, model understanding, or autonomous authority.
