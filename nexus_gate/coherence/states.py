from __future__ import annotations

from enum import StrEnum


class CoherenceState(StrEnum):
    CRITICAL = "critical"
    DEGRADED = "degraded"
    FORMING = "forming"
    COHERENT = "coherent"


def classify_coherence(score: int | float | None) -> CoherenceState:
    value = int(score if score is not None else 0)
    if value < 60:
        return CoherenceState.CRITICAL
    if value < 70:
        return CoherenceState.DEGRADED
    if value < 85:
        return CoherenceState.FORMING
    return CoherenceState.COHERENT


def coherence_status(score: int | float | None, has_missing_surfaces: bool = False) -> str:
    state = classify_coherence(score)
    if state == CoherenceState.CRITICAL:
        return "fail"
    if state == CoherenceState.COHERENT and not has_missing_surfaces:
        return "pass"
    return "warn"
