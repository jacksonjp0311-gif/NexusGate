# Triadic Geometric Lattice Protocol

Protocol packet:

```json
{
  "schema": "NEXUS_TRIADIC_GEOMETRIC_LATTICE.v2.5.0",
  "triad": {
    "evidence": "freshness and source packet admissibility",
    "geometry": "GitNexus impact and blast radius",
    "authority": "human-bound command surface"
  },
  "route_alignments": []
}
```

Each candidate route receives:

- `axes.evidence`
- `axes.geometry`
- `axes.authority`
- `alignment`
- `arbiter_adjustment`

Allowed:

- Recommend a lower-cost route.
- Penalize stale, high-blast, or weak-authority routes.
- Feed the arbiter a bounded score adjustment.

Blocked:

- `self_authorize`
- `execute_selected_action`
- `bypass_final_evolve`
- `promote_geometry_to_authority`

Final evolve remains required before commit.
