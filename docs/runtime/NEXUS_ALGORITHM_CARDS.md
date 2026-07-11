# NEXUS Algorithm Cards

NEXUS Algorithm Cards preserve the system's reusable reasoning procedures as HUD-readable and AI-readable cards.

The cards are compiled from:

```text
docs/algorithms/NEXUS_CORE_ALGORITHMS.md
```

The durable surfaces are:

```text
state/algorithms/nexus_algorithm_cards.v0.1.0.json
state/algorithms/nexus_algorithm_cards.v0.2.0.json
state/algorithms/nexus_algorithm_cards.v0.3.0.json
state/algorithms/nexus_algorithm_cards_latest.json
python -m nexus_gate.algorithms.cards --root . --json
```

## Current Discovery

Predictive Gate Timing / Runtime Pressure Model is now a first-class algorithm card.

v0.2 adds:

```text
Runtime Pressure Model
Adaptive Timeout Budgeting
Gate Selection Policy
Certificate Resume Policy
```

v0.3 adds:

```text
Predictive Evolve Planner Algorithm
```

The useful discovery is:

```text
duration history -> baseline -> drift -> anomaly -> bounded recommendation
```

This is not magic. It is a small predictive control loop: previous gate durations become priors, the current run is compared against those priors, and the system recommends a bounded timeout or cheaper next gate when pressure rises.

## Boundary

Algorithm cards describe local procedures and pressure models. They do not prove correctness, safety, security, production readiness, scientific truth, mathematical proof, model understanding, or autonomous authority.
