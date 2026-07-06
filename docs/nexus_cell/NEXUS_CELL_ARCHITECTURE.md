# NexusCell Architecture and Execution Governance Doctrine

Version: v0.8.4A-draft
Status: Doctrine / architecture / extraction map
Scope: Python-only NexusGate-native execution-containment subsystem

## 1. Mission

NexusCell is the execution containment organ of NexusGate.

NexusGate governs reflection. NexusCell governs execution. Interconnect binds the organs. Evolve decides what may compound.

```text
A sandbox contains code.
NexusCell governs execution.
```

NexusCell turns unsafe direct execution into a governed route:

```text
human intent
-> origin alignment
-> authority gate
-> containment cell
-> bounded invocation
-> execution receipt
-> continuity ledger
-> compiler/evolve visibility
-> human-authorized durable mutation
```

## 2. CubeSandbox Extraction Analysis

CubeSandbox contributes the execution-governance geometry:

```text
API gateway
-> scheduler
-> node-local runtime
-> sandbox runtime bridge
-> hypervisor / isolation backend
-> copy-on-write storage
-> network boundary
-> egress policy
-> credential injection
-> audit logs
-> snapshots
```

NexusCell does not copy CubeSandbox's Linux-native substrate. It extracts the semantic functions: fast isolation, lifecycle control, network policy, credential separation, auditability, snapshot/reversion, API-driven control, and agent-first execution semantics.

Extraction rule:

```text
Preserve the semantic function.
Replace the substrate.
Translate the language into NexusGate.
Bind it to Python.
Route it through authority.
Prove it through evidence.
```

## 3. NexusGate-Native Translation

| Sandbox term | NexusCell term |
|---|---|
| Sandbox | Containment Cell |
| Template | Origin Image |
| Snapshot | Return Seal |
| Egress | Boundary Seal |
| Credential Injection | Secret Veil |
| Audit Log | Continuity Ledger |
| Auth Callback | Authority Gate |
| Run Code | Gated Invocation |
| Policy | Gate Law |
| Output Proof | Execution Receipt |
| Rollback | Reversion |

CubeSandbox to NexusCell map:

| CubeSandbox | NexusCell |
|---|---|
| CubeAPI | Python CLI/API surface |
| CubeMaster | Cell Orchestrator |
| Cubelet | Local Runtime Manager |
| CubeShim | Runner Adapter |
| CubeHypervisor | Containment Backend |
| CubeCoW | Return Seal Layer |
| CubeVS | Boundary Seal Layer |
| CubeEgress | Boundary Seal + Secret Veil + Ledger Layer |
| Audit Log | Continuity Ledger |
| Run Command | Gated Invocation |
| Sandbox Result | Execution Receipt |

## 4. Python-Only Implementation Doctrine

NexusCell must be Python-native:

```text
Python package
Python CLI
Python policy engine
Python risk engine
Python ledger engine
Python receipt engine
Python runner abstraction
Python interconnect contract
Python tests
Python docs generation
```

Forbidden first-line implementations:

```text
No TypeScript.
No JavaScript plugin wrapper.
No AGNT packaging.
No standalone Node app.
No standalone external app first.
```

Doctrine:

```text
Python owns the decision.
Backends only perform bounded execution.
Backends do not grant authority.
Backends do not define claims.
Receipts define claims.
Ledgers preserve continuity.
Compiler visibility gates promotion.
```

## 5. Placement Requirement

```text
NexusGate/
  NexusCell/
  nexus_gate/
    nexus_cell/
  docs/
    nexus_cell/
  state/
    nexus_cell/
  ledger/
    nexus_cell/
  tests/
    test_nexus_cell_*.py
```

Initial implementation must create docs, manifest, tests, and read-only planners before any real execution backend is enabled.

## 6. Mathematical Model

```text
action = (intent, origin, authority, capability, boundary, runner, policy, context)
```

```text
ValidInvocation(action) =
  SchemaPresent(action)
  ∧ OriginAligned(action.origin)
  ∧ AuthorityDecision(action) ∈ {engage, review}
  ∧ BoundaryPolicyDeclared(action.boundary)
  ∧ ReceiptRequired(action)
  ∧ LedgerVisible(action)
```

```text
CompoundAllowed(action) =
  ValidInvocation(action)
  ∧ ExecutionReceipt.ok
  ∧ CompilerVisible(receipt)
  ∧ HumanAuthorization.present
```

## 7. Capability, Risk, and Authority Equations

Capability vector:

```text
C = [
  fs_read,
  fs_write,
  network,
  secrets,
  registry,
  process_spawn,
  service_install,
  git_write,
  host_mount,
  clipboard,
  gpu
]
```

```text
C_i ∈ {0,1}
```

Later:

```text
C_i ∈ [0,1]
```

Default weights:

```json
{
  "fs_read": 0.05,
  "fs_write": 0.25,
  "network": 0.30,
  "secrets": 0.90,
  "registry": 0.70,
  "process_spawn": 0.25,
  "service_install": 0.95,
  "git_write": 0.80,
  "host_mount": 0.60,
  "clipboard": 0.20,
  "gpu": 0.10
}
```

Risk:

```text
R(action) = Σ(w_i * C_i) + B + G + N + S
```

Where:

```text
B = blast-radius term
G = git mutation penalty
N = network openness penalty
S = secret exposure penalty
```

Authority:

```text
A(action, policy, context) =
  reject    if schema missing
  shadow    if authority missing
  review    if risk exceeds auto threshold
  engage    if authority present and risk allowed
  deny      if hard-deny policy matches
```

Thresholds:

```text
R <= 0.30          -> engage / permit
0.30 < R <= 0.65   -> review / shadow
R > 0.65           -> deny
```

Route alignment:

```text
reject
abstain
shadow
engage
defer
escalate
```

## 8. Boundary Law

```text
BoundaryDecision(request, rules):
  for rule in rules:
    if match(rule, request):
      return rule.action
  return deny
```

Rule semantics:

```text
first match wins
all declared match fields are ANDed
missing fields are wildcards
default is deny
deny emits security event
allow emits metadata receipt
```

Host wildcard semantics:

```text
*.example.com matches api.example.com
*.example.com matches a.b.example.com
*.example.com does not match example.com
```

## 9. Ledger Hashchain

```text
event_hash_i = SHA256(canonical_json(event_i_without_hashes))
```

```text
ledger_hash_i = SHA256(event_hash_i || ledger_hash_{i-1})
```

```text
ledger_hash_0 = SHA256("NEXUS_CELL_GENESIS")
```

Ledger law:

```text
No receipt without ledger reference.
No ledger event without canonical hash.
No hashchain break without rehydration warning.
```

## 10. Receipt Model

```json
{
  "receipt_id": "...",
  "cell_id": "...",
  "invocation_id": "...",
  "action": "...",
  "authority_decision": "engage",
  "risk_score": 0.22,
  "capability_vector": {},
  "runner": "dry_run_runner",
  "started_at": "...",
  "finished_at": "...",
  "exit_code": 0,
  "stdout_hash": "...",
  "stderr_hash": "...",
  "output_digest": "...",
  "policy_hash": "...",
  "ledger_hash": "...",
  "claim_boundary": "receipt proves bounded invocation record, not full security or correctness"
}
```

Receipt identity:

```text
receipt_id = SHA256(
  cell_id ||
  invocation_id ||
  stdout_hash ||
  stderr_hash ||
  ledger_hash
)
```

## 11. Return Seal Model

```json
{
  "seal_id": "...",
  "cell_id": "...",
  "origin_image_id": "...",
  "backend": "hash_only",
  "state_digest": "...",
  "created_at": "...",
  "restore_available": false,
  "claim_boundary": "hash_only seal proves state digest only; it does not prove rollback"
}
```

Backends:

```text
hash_only
windows_sandbox_ephemeral
hyperv_checkpoint
vhdx_differencing
container_layer
```

Boundary:

```text
If backend = hash_only, NexusCell may claim evidence of state, not rollback.
Only checkpoint-capable backends may claim restoration.
```

## 12. Interconnect Theory

Nodes:

```text
runtime:nexus_cell
policy:nexus_cell
ledger:nexus_cell
reports:nexus_cell
receipt:nexus_cell
boundary:nexus_cell
seal:nexus_cell
```

Edges:

```text
router:authority_gate -> runtime:nexus_cell
runtime:nexus_cell -> receipt:nexus_cell
receipt:nexus_cell -> ledger:nexus_cell
ledger:nexus_cell -> reports:local
reports:local -> feedback:engine
feedback:engine -> operator_surface
```

## 13. Evolve-Loop Integration

NexusCell adds:

```text
contain
-> invoke
-> receipt
-> ledger
-> report
```

Future evolve chain:

```text
rehydrate
-> route intent
-> verify authority
-> score capability risk
-> create containment cell
-> execute bounded invocation
-> produce receipt
-> append continuity ledger
-> emit compiler-visible report
-> interconnect result
-> surface feedback
-> human-authorized compounding
```

Formula:

```text
Evolution = Reflection + Containment + Evidence + Human Authority
```

## 14. CLI Concept

Future only. No implementation authorized by this document.

```powershell
.\scripts\nexus.ps1 cell-plan -Tag "explain intended action"
.\scripts\nexus.ps1 cell-score -Tag "requested capability"
.\scripts\nexus.ps1 cell-shadow -Tag "dry run only"
.\scripts\nexus.ps1 cell-invoke -Tag "bounded invocation" -Confirm
.\scripts\nexus.ps1 cell-receipts
.\scripts\nexus.ps1 cell-ledger
```

```text
plan may not execute.
score may not execute.
shadow may not mutate.
invoke requires explicit authority.
receipts are read-only.
ledger verify is read-only.
```

## 15. State, Docs, Ledger, and Report Concept

```text
state/nexus_cell/cell_manifest.v0.8.4.json
state/nexus_cell/policy_manifest_latest.json
state/nexus_cell/risk_profile_latest.json
state/nexus_cell/runtime_state_latest.json

ledger/nexus_cell/continuity_ledger.jsonl
ledger/nexus_cell/invocation_ledger.jsonl
ledger/nexus_cell/security_events.jsonl

reports/nexus_cell_plan_latest.json
reports/nexus_cell_risk_latest.json
reports/nexus_cell_receipt_latest.json
reports/nexus_cell_ledger_verify_latest.json

docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md
docs/nexus_cell/NEXUS_CELL_BOUNDARY_LAW.md
docs/nexus_cell/NEXUS_CELL_RISK_MODEL.md
docs/nexus_cell/NEXUS_CELL_RECEIPT_MODEL.md
docs/nexus_cell/NEXUS_CELL_RETURN_SEAL.md
```

## 16. Claim Boundaries

NexusCell is:

```text
a local development execution-governance subsystem
a containment architecture
a policy and receipt layer
a ledgered invocation path
a future rollback framework
a NexusGate-native execution organ
```

NexusCell is not:

```text
a production security proof
a perfect sandbox
a malware-proof system
an AGI system
autonomous authority
a correctness proof
a full rollback system until Return Seal backend exists
a replacement for human authorization
```

## 17. Roadmap

```text
v0.8.4A Doctrine Seal
v0.8.4B Manifest and Tests
v0.8.5 Read-Only Planner
v0.8.6 Shadow Runner
v0.8.7 Local Temp Containment Cell
v0.8.8 Boundary Seal and Secret Veil
v0.8.9 Return Seal v1
v0.9.0 Evolve Integration
```

## 18. Final Compact Laws

```text
No execution without containment.
No containment without authority.
No authority without evidence.
No evidence without ledger.
No ledger without compiler visibility.
No compounding without human authorization.
```

```text
A sandbox contains code.
NexusCell governs execution.
```

```text
Boundary before invocation.
Receipt before claim.
Ledger before memory.
Compiler before promotion.
Human before mutation.
```

Final thesis:

```text
NexusCell is the execution containment organ of NexusGate.

It extracts the agent-sandbox lifecycle intelligence of CubeSandbox,
translates it into Python-native NexusGate law,
and evolves the sandbox into a governed execution system:

authority-gated,
boundary-sealed,
receipt-emitting,
ledger-backed,
interconnect-visible,
human-authorized.
```



## v0.8.4B Portal Access and Manifest Seal

NexusCell is now visible from the Desktop Entry Portal as a doctrine and manifest surface.

```text
[10] NexusCell / Containment -> execution governance doctrine
```

This access point is read-only. It opens the local NexusCell organ, the architecture doctrine, the GitHub doctrine document, compact laws, and the manifest.

Boundary:

```text
Portal access is not execution authority.
Manifest visibility is not backend enablement.
No NexusCell backend executes until explicit implementation and human authorization.
```


## v0.8.4C Read-Only Planner Seal

NexusCell now has its first Python-native package surface:

```text
nexus_gate/nexus_cell/
python -m nexus_gate.nexus_cell.plan --root . --intent "..." --json
```

The planner converts intent into a capability vector, risk score, authority decision, route mode, and report/state evidence.

Boundary:

```text
The planner does not execute.
The planner does not spawn a user-requested process.
The planner does not create a sandbox.
The planner does not expose secrets.
The planner does not use network.
The planner does not write git.
The planner does not claim rollback.
```

## v0.8.4C1 Planner Close Note

The read-only planner upgrade exposed a stale manifest-version pin in the v0.8.4B doctrine test.

```text
wound: stale_manifest_version_pin
cause: doctrine test expected exactly v0.8.4B while the manifest advanced to v0.8.4C
doctor: update doctrine test to verify invariant boundary and portal visibility instead of freezing exact version
boundary: Doctor traps and recommends; human authorizes repair
```



## v0.8.4D Compiler Visibility Seal

NexusCell planner evidence is now visible to the gated compiler through:

```text
nexus_cell_planner_visibility
```

This gate confirms the static doctrine, manifest, package, CLI surface, and read-only planner boundary.

Boundary:

```text
Compiler visibility is not execution authority.
Compiler visibility is not containment.
Compiler visibility is not rollback.
Compiler visibility does not enable a backend.
```

## v0.8.4D1 Compiler Visibility Close Note

The compiler visibility upgrade exposed a stale planner-test manifest pin.

```text
wound: stale_planner_manifest_version_pin
cause: planner test expected exactly v0.8.4C while compiler visibility advanced the manifest to v0.8.4D
doctor: update tests to verify NexusCell v0.8.4 invariants and accepted status progression
boundary: Doctor traps and recommends; human authorizes repair
```



## v0.8.4E Failure-Mode Ledger Seal

NexusCell planner/compiler wounds are now recorded in the global Failure Mode Doctor and Failure Mode Chart.

Recorded modes:

```text
stale_manifest_version_pin
stale_planner_manifest_version_pin
compiler_visibility_not_authority
planner_visibility_not_backend_enablement
doctor_trap_without_self_authority
```

Boundary:

```text
Failure-mode visibility is not self-healing authority.
Doctor traps and recommends.
Human authorizes repair.
Compiler validates compounding.
```


## v0.8.5 Context Bridge Seal

NexusCell now emits a read-only context bridge packet:

```text
intent -> planner -> capability/risk/authority -> bounded context refs -> evidence digests -> bridge hash
```

Boundary:

```text
The context bridge does not execute.
The context bridge does not enable a backend.
The context bridge does not use network.
The context bridge does not expose secrets.
The context bridge does not mutate git.
The context bridge does not claim rollback.
The context bridge does not embed file contents by default.
```
