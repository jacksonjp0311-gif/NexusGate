# NEXUS Discovery Cards

Discovery Cards capture useful system discoveries as versioned, reproducible cards.

Each discovery card records:

```text
discovery -> math -> code function references -> algorithm card references -> replication steps -> evidence surfaces -> next versions
```

Current surface:

```text
state/discoveries/nexus_discovery_cards.v0.1.0.json
state/discoveries/nexus_discovery_cards.v0.2.0.json
state/discoveries/nexus_discovery_cards_latest.json
python -m nexus_gate.discoveries.cards --root . --json
Spiral Core Portal [18] Discoveries
```

## First Discovery

Predictive Gate Timing / Runtime Pressure Model:

```text
duration history -> baseline -> drift -> anomaly -> bounded recommendation
```

This card points to the runtime ledger, predictive timing report, algorithm cards, and implementation functions needed to replicate the discovery.

## Second Discovery

Predictive Evolve Dry-Run Planner:

```text
predictive timing -> scope classification -> gate selection -> dry-run plan -> final evolve seal required
```

This card points to the planner report, timing report, algorithm cards, and implementation functions needed to reproduce a recommendation-only next-gate plan.

## Boundary

Discovery cards preserve local engineering knowledge. They do not prove correctness, safety, security, production readiness, scientific truth, mathematical proof, or autonomous authority.
