# NEXUS Core Algorithms

## Rehydration Algorithm

```text
anchor repo -> read root README -> read docs index -> read target mini README -> inspect relevant surfaces -> patch minimal surface -> validate -> update docs/evidence if geometry changed
```

## Authority Gate Algorithm

```text
request -> actor -> requested mutation -> human authorization check -> recommend/shadow/execute lane -> block if authority missing
```

## Route Decision Algorithm

```text
StatePacket -> schema gate -> authority gate -> route map -> reject | abstain | shadow | engage | defer | escalate -> evidence record
```

## Failure Doctor Algorithm

```text
failure signal -> classify failure mode -> show compact evidence -> recommend bounded retry -> safe-clean generated residue if selected -> rerun validation
```

## Compiler Gate Algorithm

```text
required paths -> README markers -> runtime laws -> JSON parse -> mini README coverage -> failure-mode coverage -> rehydration visibility -> tests -> final status
```

## UI Surface Algorithm

```text
button click -> open bounded HUD -> read local state/evidence -> display recommendation route -> require HANDOFF for durable mutation
```

These algorithms document intended local governance flow. They are not proof of correctness, safety, security, alignment, production readiness, or real-world truth.


## Reflective Repair Algorithm

```text
failure/log/issue -> NEXUS DEEP/Mistral recommendation -> compact summary -> Y/N human gate -> bounded repair section -> tests/compiler -> commit
```

The model does not mutate files. It produces recommendation context only. The PowerShell script continues only after human approval.


## Geometric Memory Router Algorithm

```text
human intent -> Intent/Evidence/Authority/Context axes -> LFTE typed-depth projection -> EIMT drift gate -> RCMA latent remap -> TRAT attractor score -> NEXUS gate -> recommend | ask | block | bounded repair
```

Models recommend. Memory orients. Geometry constrains. Evidence gates. Humans authorize compounding.


## Geometric Runtime Packet Algorithm

```text
intent -> evidence refs -> authority mode -> context refs -> read-only geometry packet -> optional model call
```

This is the latency reducer: the model receives a compact packet instead of an unbounded repo scan.


## Geometric Preflight Cleanup Algorithm

```text
runtime smoke/test -> generated report residue -> geo-clean -> skip tracked files -> clean status surface
```

Cleanup is a preflight surface, not a repair surface. It removes generated residue only.

## Meta Loop Registry Algorithm

```text
human intent -> named loop trigger -> registry resolution -> stage execution/planning -> receipt packet -> verifier/stability lock -> human-authorized compounding only
```

The loop body is repository-owned. Generated scripts should pass intent and loop name, not regenerate the full local operating procedure.

## Predictive Gate Timing / Runtime Pressure Algorithm

```text
gate duration history -> median/p90 baseline -> latest drift ratio -> pressure classification -> bounded timeout recommendation -> cheaper next gate when pressure rises
```

This is a local predictive control loop. Prior runtimes become a lightweight forecast. The next run is compared against that forecast. If drift rises, the system recommends a bounded timeout, targeted test, or timing inspection before another expensive evolve.

It is prediction by feedback, not model-weight learning. NEXUS learns here by preserving timing evidence, comparing new runs to that evidence, and making future orchestration less wasteful.

Compact form: duration history -> baseline -> drift -> anomaly -> bounded recommendation.

## Runtime Pressure Model

```text
gate timings -> median baseline -> p90 tail estimate -> latest runtime -> drift ratio -> pressure level
```

Runtime pressure treats time as evidence. A slow pass is still a signal: it may indicate larger scope, machine load, hidden waits, or a gate becoming brittle.

## Adaptive Timeout Budgeting

```text
timeout = max(min_timeout, min(max_timeout, p90 * 1.5))
```

Timeouts are bounded budgets, not authority expansion. The recommendation may raise or lower attention on a gate, but it cannot hide failures or skip required seals.

## Gate Selection Policy

```text
changed files + runtime pressure -> cheapest valid next gate -> final evolve remains required before commit
```

If only docs changed, run docs/readme tests first. If only Electron changed, run Electron smoke first. If only Python changed, run targeted unit tests first. If runtime pressure is high, inspect predictive timing before repeating full evolve.

## Certificate Resume Policy

```text
passed gate + unchanged inputs -> certificate -> resume from active wound -> avoid rerunning green gates
```

Passed gates are local certificates for the current inputs. If a later gate fails, resume from the failed gate unless a passed gate input changed.
