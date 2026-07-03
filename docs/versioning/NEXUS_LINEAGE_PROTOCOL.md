# NEXUS GATE v0.3.7 Lineage Protocol

NEXUS GATE is evolving organically, so versioning must track module lineage rather than only a single flat version string.

Core law:

```text
Organic evolution is allowed.
Ungated compounding is not.
```

## Manifest

The current lineage manifest is:

```text
state/nexus_lineage_manifest_latest.json
```

It tracks:

```text
system_version
active_phase
parent_commit
current_commit
module_versions
interface_versions
hydration_protocol_version
feedback_protocol_version
electron_runtime_version
tui_surface_version
reflective_loop_version
last_evolve_report
last_feedback_report
last_self_healing_report
last_electron_preflight_report
last_electron_smoke_report
claim_boundaries
allowed_next_phases
blocked_promotions
```

## Purpose

The manifest lets an AI or human know:

```text
what version this is
what changed
what passed
what failed
what is allowed next
what is blocked
what is only scaffolded
what is production-ready or not
```

## Boundary

Lineage is orientation evidence. It does not prove correctness, safety, security, production readiness, model understanding, or autonomous authority.
