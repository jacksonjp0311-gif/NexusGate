# CubeSandbox to NexusCell Port Map

| CubeSandbox Pattern | NexusCell Translation |
|---|---|
| CubeAPI | NexusCell Python CLI/API surface |
| CubeMaster | Cell Orchestrator |
| Cubelet | Local Runtime Manager |
| CubeShim | Runner Adapter |
| CubeHypervisor | Containment Backend |
| CubeCoW | Return Seal Layer |
| CubeVS | Boundary Seal Layer |
| CubeEgress | Boundary Seal + Secret Veil + Ledger Layer |
| Template | Origin Image |
| Snapshot | Return Seal |
| Sandbox | Containment Cell |
| Audit Log | Continuity Ledger |
| Credential Injection | Secret Veil |
| Egress Rules | Boundary Law |
| Run Command | Gated Invocation |
| Sandbox Result | Execution Receipt |

Boundary: this is an architecture translation, not a claim that KVM/RustVMM/containerd/eBPF/OpenResty are running locally.
