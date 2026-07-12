# Evidence Distillation Graph Protocol

Packet:

```json
{
  "schema": "NEXUS_EVIDENCE_DISTILLATION_GRAPH.v2.6.0",
  "nodes": [],
  "edges": [],
  "pruning_policy": {},
  "emergence": {}
}
```

Node contract:

- `node_id`
- `node_type`
- `summary`
- `source_surface`
- `source_hash`
- `confidence`
- `claim_boundary`
- `links`
- `prunable`
- `retention_policy`

Blocked:

- prune source/docs/tests
- prune without source hash
- prune without distillation node
- self-authorize pruning
- bypass final evolve
