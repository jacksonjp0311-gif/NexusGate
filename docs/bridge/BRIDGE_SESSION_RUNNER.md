# Bridge Session Runner

The bridge session runner is the first bounded local bridge path.

## Flow

```text
raw event
  -> LocalDemoAdapter
  -> StatePacket
  -> NexusRouter
  -> ReceptorManifest
  -> CompatibilityDecision
  -> BridgeSessionReport
```

## Laws

```text
No bridge session without adapter normalization.
No bridge session without route decision.
No bridge session without receptor compatibility.
No bridge report without claim boundary.
```

## BridgeSessionReport

A `BridgeSessionReport` records:

```text
session_id
packet_id
adapter_id
receptor_id
route_mode
route_reason
compatibility_mode
compatibility_reason
final_mode
final_reason
claim_boundary
```

## Local outcomes

| Input | Router | Receptor Compatibility | Final |
|---|---|---|---|
| read-only demo message | engage | compatible | engage |
| tool call without authority | shadow | shadow | shadow |
| unsupported schema | reject | reject | reject |

Boundary: bridge session evidence is local development evidence only. It does not prove production interoperability.
