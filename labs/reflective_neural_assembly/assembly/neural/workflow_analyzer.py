from __future__ import annotations

from statistics import mean
from typing import Any

from .pattern_engine import detect_pattern


def analyze_workflow(events: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(events)
    failures = [event for event in events if not event.get("success")]
    durations = [float(event.get("duration_ms", 0.0)) for event in events]
    failure_rate = len(failures) / total if total else 0.0
    duration_pattern = detect_pattern(durations)
    avg_duration = mean(durations) if durations else 0.0
    risk = min(1.0, failure_rate * 0.7 + (0.2 if duration_pattern.get("pattern") == "trend" and duration_pattern.get("slope", 0) > 0 else 0.0))
    return {
        "execution_count": total,
        "failure_count": len(failures),
        "failure_rate": round(failure_rate, 3),
        "avg_duration_ms": round(avg_duration, 2),
        "duration_pattern": duration_pattern,
        "next_execution_risk": round(risk, 3),
        "recommendations": _recommendations(failure_rate, duration_pattern),
    }


def _recommendations(failure_rate: float, duration_pattern: dict[str, Any]) -> list[str]:
    recs: list[str] = []
    if failure_rate > 0.25:
        recs.append("Inspect recent failures and run governed diagnostic lanes before retrying.")
    if duration_pattern.get("pattern") == "trend" and duration_pattern.get("slope", 0) > 0:
        recs.append("Duration appears to be increasing; compare recent logs and pack/report sizes.")
    if not recs:
        recs.append("Continue observing; no high-pressure workflow pattern detected.")
    return recs
