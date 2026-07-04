from __future__ import annotations

from statistics import mean, pstdev
from typing import Any


def _slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    xs = list(range(len(values)))
    mx = mean(xs)
    my = mean(values)
    denom = sum((x - mx) ** 2 for x in xs) or 1.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, values)) / denom


def detect_pattern(values: list[float]) -> dict[str, Any]:
    values = [float(v) for v in values]
    if len(values) < 3:
        return {"pattern": "unknown", "confidence": 0.2, "scores": {}}
    span = max(values) - min(values)
    std = pstdev(values) if len(values) > 1 else 0.0
    slope = _slope(values)
    diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
    largest_step = max((abs(item) for item in diffs), default=0.0)
    alternating = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i - 1] < 0)
    scores = {
        "trend": min(abs(slope) / (span + 1e-9) * len(values), 1.0) if span else 0.0,
        "stationary": 1.0 - min(std / (abs(mean(values)) + 1e-9), 1.0) if values else 0.0,
        "step": min(largest_step / (span + 1e-9), 1.0) if span else 0.0,
        "seasonal": alternating / max(len(diffs), 1),
        "chaotic": min(std / (span + 1e-9), 1.0) if span else 0.0,
    }
    pattern = max(scores, key=scores.get)
    confidence = round(scores[pattern], 3)
    if confidence < 0.35:
        pattern = "unknown"
    return {"pattern": pattern, "confidence": confidence, "scores": {k: round(v, 3) for k, v in scores.items()}, "slope": round(slope, 4)}
