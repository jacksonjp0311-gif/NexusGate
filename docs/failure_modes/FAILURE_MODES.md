# NEXUS GATE Failure Modes

| Failure mode | Meaning | Required response |
|---|---|---|
| `schema_missing` | Packet lacks schema identity. | Reject. |
| `authority_unverified` | Requested action lacks authority. | Shadow or reject. |
| `origin_dehydrated` | Session state drifted from repo origin. | Rehydrate before mutation. |
| `compiler_failed` | Repo state failed gated compiler. | No commit or promotion. |
| `mini_readme_missing` | Target folder lacks local orientation. | Repair mini README before patching. |
| `ledger_unavailable` | Evidence cannot be appended. | Block compounding. |
| `direct_compiler_call_missing` | Runtime script does not call compiler directly. | Repair script. |
| `claim_boundary_missing` | Report lacks non-claim boundary. | Block public-facing claim. |
| `shadow_failure_unrouted` | Shadow failure has no wound/failure route. | Convert to failure-mode record. |
| `replay_missing` | Re-engagement lacks replay certificate. | Block re-engagement. |

Boundary: failure-mode classification is local development evidence. It is not a safety proof.
