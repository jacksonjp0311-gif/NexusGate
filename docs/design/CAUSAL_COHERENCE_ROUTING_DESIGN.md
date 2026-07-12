# Causal Coherence Routing Design

NEXUS GATE v2.1 makes the coherence field causal.

Before v2.1, Decision Envelope selected a route and Coherence Field described the operating field. In v2.1, the decision path becomes:

```text
reports -> recommendations -> coherence field -> arbiter score -> selected action
```

## Design Goal

Seek coherence under pressure without turning coherence into authority.

The arbiter scores recommendations by urgency, evidence, confidence, cost, risk, stale evidence, and coherence pressure.

```text
score = severity + source_priority + confidence - cost - blockers - stale_penalty + coherence_adjustment
```

## Pressure Behavior

When coherence drops, missing surfaces appear, lineage entropy rises, or runtime pressure increases, the arbiter prefers orientation and repair routes before mutation routes.

## Boundary

```text
coherence may steer recommendations
coherence may not execute recommendations
coherence may not grant authority
final evolve remains required before commit
```
