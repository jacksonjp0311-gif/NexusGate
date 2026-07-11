# NEXUS Cortex Integration

Cortex is imported as a root-local subsystem at `Cortex/`. It is a local-first repository assimilation and selective-memory engine for coding agents. In NEXUS GATE it acts as a bounded evidence organ: it can index, retrieve, route, activate sparse repository context, and emit NexusGate-shaped packets, but it cannot authorize mutation or bypass NEXUS gates.

## Current Bootstrap Result

The first NEXUS bootstrap used a repo-local Cortex home at `state/cortex_memory/`, which is intentionally ignored because it contains a large SQLite runtime database. Cortex indexed 3,249 eligible files with full index coverage, compiled 16,898 neural synapses, and detected 129 unsupported or excluded files.

The bootstrap certificate status is currently `degraded` because the repository changed during/after assimilation and the observed manifest hash drifted. That is a useful safety behavior: Cortex fell back to `read_only` governor mode instead of claiming authority.

## Benchmarks

Latest local benchmark summary:

| Check | Result |
|---|---:|
| Cortex unit tests | 22 passed |
| Thalamus route plan | 0.337 s |
| NEXUS verify | 20.452 s |
| Sparse interlink | 10.063 s |
| NEXUS packet | 3.489 s |
| Activation with auto-refresh | 40.906 s |
| Sparse benchmark | 262 nodes, 280 synapses, 24 fired nodes |
| Thalamus before/after | target rank improved 4 -> 3, top-3 recall 0% -> 100% |

The self-host lifecycle benchmark did not run from the vendored copy because `self_host_benchmark.py` performs `git clone --no-local` from the active Cortex folder, and the imported `Cortex/` copy intentionally excludes `.git`. Run that benchmark from the original Git-backed Cortex repository when needed.

## High-Value Integration Path

1. Add a `cortex` NEXUS lane that wraps `python -m cortex --home state/cortex_memory`.
2. Add a Cortex compiler gate that checks database integrity, manifest freshness, governor mode, and packet shape.
3. Feed Cortex `nexus-packet` output into Meta-Orchestrator as a recommendation source.
4. Add Electron read-only visibility for Cortex status, top activated paths, and governor state.
5. Keep final authority in NEXUS: Cortex may recommend context; NEXUS gates and the human authorize durable mutation.

## Claim Boundary

Cortex integration is local development evidence only. It does not prove correctness, safety, security, production readiness, biological fidelity, model understanding, or autonomous authority.
