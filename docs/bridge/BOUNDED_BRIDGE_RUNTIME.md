# Bounded Bridge Runtime

The bounded bridge runtime is the first v0.2.0 runtime surface.

## Flow

```text
raw event batch
  -> BoundedBridgeRuntime
  -> BridgeSessionRunner
  -> BridgeSessionReport
  -> BoundedRuntimeReport
```

## Laws

```text
No runtime without event limit.
No runtime without bridge session reports.
No runtime without summary counts.
No runtime without claim boundary.
No promotion without runtime compiler pass.
```

## BoundedRuntimeReport

A `BoundedRuntimeReport` records:

```text
runtime_id
max_events
input_count
processed_count
truncated_count
summary_counts
session_reports
claim_boundary
```

## Local expected counts

```text
engage = 1
shadow = 1
reject = 1
```

Boundary: bounded runtime evidence is local development evidence only. It does not prove production interoperability.
