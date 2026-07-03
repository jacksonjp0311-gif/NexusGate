# LocalDemoAdapter

`LocalDemoAdapter` is the first demo adapter for NEXUS GATE.

It proves this local route:

```text
raw local demo event
  -> LocalDemoAdapter.normalize_event()
  -> StatePacket
  -> NexusRouter.route()
  -> RouteDecision
```

## Supported events

```text
demo.message
demo.tool_request
```

## Supported actions

```text
read_only_signal
tool_call
```

`tool_call` still requires authority scope or it shadows. `read_only_signal` may engage.

Boundary: LocalDemoAdapter is not a real external framework integration.
