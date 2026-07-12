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

## Coherence Field Algorithm

```text
origin + decision envelope + memory + runtime pressure + policy + wounds + certificates + git scope -> coherence score + continuity recommendation
```

The Coherence Field is a shared state-space for NEXUS organs. It measures orientation, entropy, stale surfaces, policy visibility, and selected next action while preserving the law that coherence may guide routing but may not grant authority.

## Governed Agent Continuity Algorithm

```text
intent packet -> origin certificate -> evidence packet -> authority decision -> human authorization -> controlled invocation -> receipt -> validation certificate or wound -> memory promotion decision -> continuation packet
```

The continuity algorithm turns NEXUS into a portable protocol for AI-to-repo and human-to-AI work. It preserves context across sessions without granting implicit authority to models, memory, HUDs, or compilers.

## Causal Coherence Routing Algorithm

```text
candidate recommendations + coherence field -> arbiter scoring -> selected route -> human authorization -> final evolve seal
```

Causal Coherence Routing lets field pressure affect recommendation selection. Low coherence, high entropy, stale evidence, missing policy, active wounds, and runtime pressure increase orientation/repair recommendations without granting execution authority.

## Causal Loop Hardening Algorithm

```text
repository snapshot -> typed coherence state -> normalized wounds -> clamped confidence -> fresh packet scoring -> deterministic route
```

Causal Loop Hardening prevents edge-case routing drift. A score of zero remains critical, inactive wound sentinels do not trigger repair routes, confidence cannot exceed one, and tied routes resolve deterministically. Snapshot epochs make stale packet use visible before route selection.

## Triadic Geometric Lattice Algorithm

```text
candidate recommendation -> evidence axis + geometry axis + authority axis -> geometric mean alignment -> arbiter adjustment -> selected route
```

Triadic Geometric Lattice turns routing into a three-axis field. Evidence asks whether packet inputs are fresh; geometry asks whether the route is low-blast and aligned with GitNexus impact; authority asks whether the command remains inside governed human-bound surfaces.

```text
alignment = cuberoot(evidence * geometry * authority)
arbiter_adjustment = (alignment - 0.65) * 18
```

The lattice may optimize route selection. It may not grant authority, mutate files, execute commands, or replace final evolve.

## Outcome Feedback Algorithm

```text
selected recommendation -> observed gate result -> outcome ledger -> route fitness -> calibration packet
```

A recommendation becomes useful intelligence only after an outcome is recorded. The outcome may tune future route pressure, but it may not authorize execution or skip final evolve.

## Evidence Distillation Algorithm

```text
heavy evidence -> source hash -> compact node -> graph link -> provenance-preserving memory
```

Evidence Distillation compresses large reports, state packets, ledgers, and cards into smaller graph nodes. The node keeps summary fields, source hash, source surface, confidence, retention policy, and claim boundary so Codex can rehydrate from compact graph memory before opening heavy files.

## Provenance-Preserving Pruning Algorithm

```text
artifact -> distillation node exists -> source hash exists -> retention rule -> pruning recommendation -> human authorization
```

Pruning is recommendation-only. Source, docs, tests, policy, manifests, and current latest evidence are protected. Runtime exhaust may be recommended for pruning only after distillation.

## Concept Graph Compression Algorithm

```text
many evidence nodes -> recurring relationship -> compact concept node -> future rehydration pointer
```

Concept graph compression uses repeated links across routes, outcomes, coherence, cards, and runtime pressure to expose higher-order concepts without rereading every raw artifact.

## Emergence Detection Algorithm

```text
graph motifs + recurrence + pressure + outcomes -> discovery candidate
```

Emergence detection identifies recurring route/coherence/outcome motifs as discovery candidates. It does not claim truth; it creates a candidate card path that still requires evidence and gates.

## Arbiter Calibration Algorithm

```text
recommendation outcomes by source -> source reliability -> weight adjustment -> next arbiter score
```

Calibration estimates whether a recommendation source has historically helped. It adjusts pressure softly and remains bounded by human authority.

## Pressure Memory Algorithm

```text
coherence score samples -> rising/falling/stable trend -> hysteresis-aware routing signal
```

Pressure memory prevents route flapping by requiring persistent pressure changes before changing route class.

## Runtime Churn Hygiene Algorithm

```text
git status -> allowlisted generated tracked surfaces -> allowlisted untracked exhaust -> source dirty remains visible -> optional bounded clean
```

Runtime hygiene prevents generated evidence exhaust from masking source mutations. It may restore known generated surfaces and remove known timestamped pack exhaust; it may not clean unclassified files, run unbounded git clean, or erase source changes.

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

## Epoch Integrity Seal Algorithm

```text
canonical source files -> source Merkle root -> parent epoch + runtime contract -> epoch id -> immutable epoch directory -> append-only chain
```

Epoch Integrity gives graph learning a stable timebase without making Git commit SHA the primary identity. Generated evidence can be committed after it is produced, so NEXUS uses source-root identity first and stores commit SHA as advisory attestation.

## Source Epoch Identity Algorithm

```text
canonical source + relevant untracked source + runtime contract + schema compatibility -> source epoch id
```

Source Epoch identity changes only when source content or compatibility rules change. Re-running observation against unchanged source reuses the same Source Epoch.

## Epoch Observation Algorithm

```text
source epoch -> gate report hashes + dirty state + runtime state + producer version -> observation event -> observation ledger
```

Observation records what was seen during a run without fabricating a new developmental epoch.

## Append-Only Ledger Transaction Algorithm

```text
lock -> verify tail -> build event -> previous hash -> event hash -> append -> fsync -> verify tail
```

Ledger events are hash-linked JSONL rows. Latest files are convenience pointers; hash chains are the durable event memory.

## Command Registry Resolution Algorithm

```text
selected route -> command registry id -> fixed executor target -> normalized arguments -> bounded registered lane
```

Raw shell strings are not authority objects. Registered command resolution makes action receipts bind to known NEXUS lanes only.

## Human Authorization Binding Algorithm

```text
recommendation receipt -> explicit human authorization -> command id + args hash + pre-epoch binding -> single-action authority receipt
```

Authorization is explicit evidence. It is not inferred from command invocation, success, process existence, model output, or previous authorization.

## Causal Action Lifecycle Algorithm

```text
PROPOSED -> AUTHORIZED -> EXECUTING -> EXECUTED -> VALIDATED -> LEARNABLE
```

Invalid transitions are rejected and recorded. Recommendation is not execution, execution is not validation, and validation is not durable learning without causal confidence.

## Effect-Set Comparison Algorithm

```text
predicted write set + expected effects -> actual changed surfaces -> unexpected writes + precision/recall + confounder pressure
```

Unexpected writes remain visible and can block learning.

## Causal Confidence Algorithm

```text
K = epoch_integrity * authorization_binding * execution_binding * write_agreement * validation_coverage * (1 - confounder_pressure)
```

Hard failures set causal confidence to zero. Learnability requires high confidence and admissible pre/post epochs.

## Receipt-Gated Calibration Algorithm

```text
validated learning receipt -> bounded route model update -> replay-safe calibration ledger
```

No receipt means no learning. Working-tree-only epochs, duplicate receipts, validation failures, and confounded effects do not update durable route fitness.
