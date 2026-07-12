# Outcome-Aware Arbiter Design

NEXUS GATE v2.2 closes the route feedback loop.

```text
selected recommendation -> observed gate result -> route fitness -> arbiter calibration -> next recommendation
```

The arbiter does not learn by changing model weights. It learns by recording route outcomes as repository-native evidence.

## Route Fitness

```text
route_fitness = outcome_score + coherence_bonus
```

Where outcome score is bounded:

```text
pass=1.0, warn=0.65, skipped=0.35, unknown=0.25, fail=0.0
```

## Calibration

```text
source_reliability = (passes + 0.5 * warnings) / runs
weight_adjustment = (source_reliability - 0.5) * 12
```

Calibration may tune recommendation pressure. It may not authorize execution.
