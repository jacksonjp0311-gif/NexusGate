# COLD EVIDENCE ENGINE — v0.1.5

The cold evidence engine handles slow-path evidence after a route enters shadow, fails, or requires retrust.

## Contracts

| Contract | Purpose |
|---|---|
| `ShadowReport` | Records the result of a shadow route. |
| `ShadowFailure` | Converts a failed shadow report into a classified failure. |
| `ShadowWound` | Persists a failure as a wound that blocks trust promotion. |
| `WoundRoute` | Declares the recovery route for a wound. |
| `ReplayCertificate` | Records replay evidence before retrust. |
| `DemotionDecision` | Records demotion, retirement, or recalibration. |

## Laws

```text
No shadow failure without wound route.
No re-engagement without replay certificate.
No specialist promotion without cold evidence.
No memory promotion from failed shadow evidence.
```

Boundary: cold evidence is local governance evidence. It does not prove safety, security, correctness, or production readiness.
