# Route Calibration Protocol

Route calibration is receipt-gated.

No validated learning receipt means no route learning.

Calibration rules:

- One success cannot strongly promote a route.
- Failures weigh more than successes.
- Updates are capped.
- Duplicate receipts cannot recalibrate twice.
- Working-tree-only epochs cannot update durable calibration.
- Coherence score is not automatic proof of route success.

Calibration estimates execution reliability, prediction accuracy, causal confidence, validation success, and uncertainty separately.
