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

## Predictive Evolve Planner Algorithm

```text
predictive timing -> scope classification -> gate selection -> dry-run plan -> final evolve seal required
```

Predictive Evolve turns the runtime pressure model into a bounded planning envelope. It recommends the cheapest useful next gate for the current scope, records the plan as evidence, and keeps the authority line clear: it does not execute the plan, mutate the repo, or replace full evolve before commit.

## Cortex Sync Protocol Algorithm

```text
local Cortex source -> exclude runtime/secrets/cache/git surfaces -> copy source/docs/tests/benchmarks -> write sync report -> run Cortex gate -> preserve read-only authority
```

The sync protocol turns Cortex upgrades into a repeatable bounded lane. It imports local source artifacts only and keeps runtime memory, secrets, git history, external APIs, and mutation authority outside the transfer.

## Versioned Vector Blob Storage Algorithm

```text
float vector -> finite-value check -> CTXV1 magic header -> little-endian float32 payload -> migration/status report -> retrieval deserialization
```

Cortex vector storage converts legacy JSON vectors into compact versioned binary payloads. The algorithm reduces vector payload size and gives the gate a format-status signal without changing authority or claiming semantic correctness.

## Predictive Memory Orchestrator Algorithm

```text
Cortex gate + Cortex benchmark + algorithm cards + discovery cards + predictive evolve plan -> memory-aware recommendation -> trend ledger -> final evolve seal required
```

Predictive Memory Orchestration fuses repository memory health with runtime gate planning. Cortex tells NEXUS whether memory is indexed, bounded, and vector-current; predictive evolve tells NEXUS the cheapest next validation path; cards tell Codex which reusable reasoning patterns exist. The output is a recommendation-only next step and a benchmark trend row, never autonomous execution.

## Cortex Certificate Refresh Algorithm

```text
index -> telemetry -> graph rebuild -> vector migration -> verify certificate -> activate refresh -> doctor -> NEXUS packet
```

Cortex Certificate Refresh updates the local memory substrate after repo drift. It refreshes evidence and certificate status without granting Cortex mutation authority or replacing NEXUS evolve gates.

## Origin Seal Algorithm

```text
README current line + package versions + lineage + key report hashes + commit SHA -> origin manifest hash -> current product identity
```

Origin Seal distinguishes current product identity from subsystem lineage. Older package, API, and report versions remain visible as lineage instead of being mistaken for the current product origin.

## Authority Monotonicity Algorithm

```text
A_out = A_in intersection policy_allowed; reject if any adapter, model, memory, UI, compiler, or certificate increases authority
```

Authority may stay equal or decrease as packets move through NEXUS. No interface, memory surface, recommendation, compiler result, or visualization may manufacture new authority.

## Evidence Freshness Algorithm

```text
schema valid + origin hash match + producer compatible + relevant inputs unchanged + freshness policy satisfied -> admissible evidence
```

Files are stronger than stdout, but stale files are not current truth. Evidence becomes admissible only when its origin and freshness survive the current gate policy.

## Gate Dependency Invalidation Algorithm

```text
prior pass + relevant input hashes unchanged + toolchain unchanged + gate contract unchanged -> reusable certificate; otherwise invalidate
```

Certificate reuse must depend on actual gate inputs, not just a prior green line. This turns passed gates into bounded computational assets without skipping the final evolve seal.

## Decision Envelope Arbitration Algorithm

```text
toolbelt + preflight + wounds + timing + predictive memory + certificates -> normalized recommendations -> selected next action
```

The next intelligence layer is not another recommender. It is an arbiter that normalizes recommendation packets, compares cost/risk/evidence, and selects one bounded next step.

## Self Bootstrap Decision Envelope Algorithm

```text
origin seal + Cortex memory + predictive gates + wounds + certificates + git scope -> canonical decision envelope -> human-authorized next step
```

Self Bootstrap means the repo can wake itself into an oriented state for Codex, chat, TUI, or Electron without granting itself authority. The packet selects a next action as recommendation-only evidence; it never executes the action or replaces final evolve.

## Causal Memory Closure Algorithm

```text
memory -> recommendation -> authorized action -> receipt -> outcome evidence -> memory promotion or wound
```

Memory should become causal only through evidence. Successful authorized actions may become future memory candidates; failed actions become wounds until replay closes them.

## Controlled Lane Receipt Algorithm

```text
named lane -> policy check -> human authorization -> bounded execution -> stdout/stderr digests -> receipt hash -> ledger event
```

Controlled lanes turn local execution into evidence-bearing action. The receipt records what ran and under which authority boundary without becoming arbitrary shell authority.

## Lineage Topology Algorithm

```text
module versions + interface versions + commits + reports + blocked promotions -> origin and lineage map
```

Lineage topology lets an agent distinguish product identity, subsystem versions, scaffolded surfaces, blocked promotions, and stale reports before compounding.

## Repo-Native Memory Promotion Algorithm

```text
candidate lesson -> provenance -> evidence -> gate pass -> claim boundary -> lineage entry -> durable card or memory surface
```

NEXUS does not learn by changing model weights. It learns by promoting evidence-qualified lessons into repository-native surfaces that future sessions can rehydrate.
