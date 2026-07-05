# EIMT Runtime Memory Contract for NexusGate v0.8.3A

## Minimal Runtime Contract

Nexus memory must be source-bounded, drift-gated, and replay-auditable before it can guide repair.

## Required Modules

```text
Episode
MemoryStore
MetricManifest
RetrievalEngine
DriftGate
SourceFallback
ReplayEvaluator
SimulationGuard
BaselineHarness
BenchmarkRunner
ScoringModule
EvidencePackageCompiler
```

## Episode Shape

```json
{
  "id": "episode-id",
  "context": "why this was recorded",
  "content": "bounded memory text",
  "source_ref": "file/test/log/commit reference",
  "ledger_ref": "append-only evidence ref",
  "fingerprint": "stable hash or invariant",
  "drift_score": 0.0,
  "classification": "candidate|validated|downgraded|blocked"
}
```

## Retrieval Rule

High-drift memory cannot be returned as fact. It must fall back to source, uncertainty, or human clarification.

## Promotion Rule

Memory promotion requires reproducible utility, source reference, drift score, and evidence package.
