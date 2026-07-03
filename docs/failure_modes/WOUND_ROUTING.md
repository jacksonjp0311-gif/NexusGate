# Wound Routing

Wound routing is the required response to failed shadow execution.

## Flow

```text
ShadowReport
  -> ShadowFailure
  -> ShadowWound
  -> WoundRoute
  -> ReplayCertificate
  -> DemotionDecision | Recalibration | Retrust
```

## Required Contracts

- ShadowReport
- ShadowFailure
- ShadowWound
- WoundRoute
- ReplayCertificate
- DemotionDecision

## Rules

```text
No wound route, no retrust.
No replay certificate, no re-engagement.
No demotion decision without failure evidence.
```

Boundary: wound routing improves local recovery discipline. It does not prove safety, security, correctness, or production readiness.
