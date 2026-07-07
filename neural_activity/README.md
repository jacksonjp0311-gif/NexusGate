# Neural Activity

Canonical status: v0.1.1 visual organ.

This folder contains the Neural Cathedral visual program used by NexusGate.

## Runtime surfaces

- `index.html` â€” full standalone Neural Cathedral program.
- HUD preview â€” `electron/renderer/index.html` embeds `index.html?embed=1`.
- OPEN control â€” launches the full standalone program.

## Boundary

Neural Activity is a visual surface only.

It does not change:
- model authority
- NexusCell execution authority
- governance policy
- memory policy
- filesystem mutation authority

## Rehydration note

AA is the canonical architecture:

```text
small HUD panel = live embedded source program
OPEN = full standalone source program
surrogate previews = deprecated
```

v0.1.1 locks that knowledge so a future system does not repeat the Y/Z surrogate path.
