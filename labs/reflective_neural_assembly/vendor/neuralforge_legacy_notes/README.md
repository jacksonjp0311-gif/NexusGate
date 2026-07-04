# NeuralForge Legacy Notes

Reference source:

```text
https://github.com/jacksonjp0311-gif/-NeuralForge
```

Adapted concepts:

- SmartEngine decision modes: retry, optimize, predict, pattern, fix, analyze
- PatternEngine telemetry analysis: trend, seasonal, stationary, chaotic, step, unknown
- DataLearner as optional local neural learning only
- WorkflowAnalyzer for execution history and lane risk
- RealtimeEvolutionEngine for rolling health, alerts, predictions, recommendations, knowledge entries
- AGNT bridge event normalization into execution telemetry

NEXUS conversion:

```text
Observe -> Learn -> Predict -> Recommend -> Gate -> Human authorizes -> Execute through governed NEXUS lanes
```

Blocked conversion:

```text
auto-apply fixes
arbitrary shell execution
external API writes
secret access
parent repo mutation
self-authorization
```
