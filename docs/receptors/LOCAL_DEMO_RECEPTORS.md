# Local Demo Receptors

Local demo receptors prove the second half of the bridge path:

```text
LocalDemoAdapter
  -> StatePacket
  -> ReceptorManifest
  -> CompatibilityDecision
```

## Receptors

```text
local.demo.readonly
local.demo.tool_shadow
```

`local.demo.readonly` accepts `read_only_signal`.

`local.demo.tool_shadow` accepts `tool_call`, but requires authority. Without authority, the compatibility decision is `shadow`.

Boundary: local demo receptors are not real external framework targets.
