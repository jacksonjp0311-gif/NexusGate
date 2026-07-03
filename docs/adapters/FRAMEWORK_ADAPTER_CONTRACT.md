# Framework Adapter Contract

Every framework must enter through an adapter.

Required adapter functions:

```text
detect_capabilities()
normalize_event(raw_event) -> StatePacket
export_receptors()
supports_shadow()
emit_disengagement_receipt()
```

Runtime law:

```text
No adapter, no bridge.
```