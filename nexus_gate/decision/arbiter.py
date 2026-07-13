from __future__ import annotations

from typing import Any

from nexus_gate.coherence.states import CoherenceState, classify_coherence


SCHEMA = "NEXUS_RECOMMENDATION_ARBITER.v2.5.0"

SEVERITY_WEIGHT = {
    "required": 55,
    "critical": 50,
    "high": 38,
    "medium": 26,
    "info": 12,
}

COST_PENALTY = {
    "short": 2,
    "bounded": 5,
    "medium": 10,
    "long": 24,
}

SOURCE_PRIORITY = {
    "origin-seal": 30,
    "wound-compression": 28,
    "preflight": 24,
    "coherence-field": 22,
    "predictive-memory": 20,
    "git-scope": 18,
    "certificate-resume": 16,
    "predictive-timing": 14,
    "predictive-evolve": 12,
    "final-seal": 8,
}


def _coherence_adjustment(recommendation: dict[str, Any], coherence: dict[str, Any]) -> int:
    raw_score = (coherence.get("coherence") or {}).get("score")
    score = int(raw_score if raw_score is not None else 0)
    state = classify_coherence(score)
    entropy = int(((coherence.get("coherence") or {}).get("lineage_entropy")) or 0)
    source = recommendation.get("source")
    adjustment = 0
    if state in {CoherenceState.CRITICAL, CoherenceState.DEGRADED}:
        if source in {"origin-seal", "coherence-field", "preflight"}:
            adjustment += 18
        if source == "final-seal":
            adjustment -= 20
    if entropy >= 8 and source in {"origin-seal", "coherence-field", "git-scope"}:
        adjustment += 8
    if ((coherence.get("coherence") or {}).get("missing_surfaces")) and source == "coherence-field":
        adjustment += 16
    return adjustment


def _calibration_adjustment(recommendation: dict[str, Any], calibration: dict[str, Any] | None = None) -> float:
    calibration = calibration or {}
    source = recommendation.get("source") or "unknown"
    source_calibration = calibration.get("source_calibration") or {}
    return float((source_calibration.get(source) or {}).get("weight_adjustment") or 0.0)


def _confidence(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = 0.0
    return max(0.0, min(1.0, parsed))


def _conductance_adjustment(recommendation: dict[str, Any]) -> float:
    field = recommendation.get("conductance_field") or {}
    if not field:
        return 0.0
    try:
        adjustment = float(field.get("bounded_adjustment") or 0.0)
    except (TypeError, ValueError):
        adjustment = 0.0
    return max(-6.25, min(6.25, adjustment))


def score_recommendation(
    recommendation: dict[str, Any],
    coherence: dict[str, Any] | None = None,
    calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coherence = coherence or {}
    confidence = _confidence(recommendation.get("confidence"))
    severity = SEVERITY_WEIGHT.get(str(recommendation.get("severity", "info")), 10)
    source = SOURCE_PRIORITY.get(str(recommendation.get("source", "")), 8)
    cost = COST_PENALTY.get(str(recommendation.get("estimated_cost", "bounded")), 6)
    blockers = len(recommendation.get("blocking_conditions") or [])
    freshness = recommendation.get("source_packet_freshness") or {}
    stale_penalty = 0
    if recommendation.get("source") != "final-seal":
        if recommendation.get("source_packet_hash") is None:
            stale_penalty += 8
        if freshness.get("fresh") is False:
            stale_penalty += 10
    final_guard = 0
    if recommendation.get("source") == "final-seal":
        # Final evolve is mandatory before commit, but not usually the cheapest next routing action.
        final_guard = -18
    calibration_boost = _calibration_adjustment(recommendation, calibration)
    lattice = recommendation.get("triadic_lattice") or {}
    lattice_adjustment = float(lattice.get("arbiter_adjustment") or 0.0)
    conductance_adjustment = _conductance_adjustment(recommendation)
    total = round(severity + source + (confidence * 20) + _coherence_adjustment(recommendation, coherence) + calibration_boost + lattice_adjustment + conductance_adjustment - cost - blockers - stale_penalty + final_guard, 3)
    scored = dict(recommendation)
    scored["arbiter_score"] = total
    scored["arbiter_factors"] = {
        "severity_weight": severity,
        "source_priority": source,
        "confidence_weight": round(confidence * 20, 3),
        "cost_penalty": cost,
        "blocking_penalty": blockers,
        "stale_penalty": stale_penalty,
        "coherence_adjustment": _coherence_adjustment(recommendation, coherence),
        "calibration_adjustment": calibration_boost,
        "triadic_lattice_adjustment": lattice_adjustment,
        "conductance_adjustment": conductance_adjustment,
        "final_guard": final_guard,
    }
    return scored


def arbitrate_recommendations(
    recommendations: list[dict[str, Any]],
    coherence: dict[str, Any] | None = None,
    calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not recommendations:
        raise ValueError("Cannot arbitrate an empty recommendation set.")
    scored = [score_recommendation(item, coherence, calibration) for item in recommendations]
    selected = max(
        scored,
        key=lambda item: (
            item["arbiter_score"],
            SEVERITY_WEIGHT.get(str(item.get("severity", "info")), 0),
            SOURCE_PRIORITY.get(str(item.get("source", "")), 0),
            str(item.get("source", "")),
            str(item.get("action", "")),
        ),
    )
    return {
        "schema": SCHEMA,
        "mode": "triadic_causal_lattice_routing",
        "selected": selected,
        "scored_recommendations": scored,
        "coherence_input": {
            "status": (coherence or {}).get("status", "unknown"),
            "score": ((coherence or {}).get("coherence") or {}).get("score"),
            "lineage_entropy": ((coherence or {}).get("coherence") or {}).get("lineage_entropy"),
        },
        "calibration_input": {
            "schema": (calibration or {}).get("schema"),
            "sources": sorted(((calibration or {}).get("source_calibration") or {}).keys()),
        },
        "lattice_input": {
            "routes_with_alignment": len([item for item in scored if item.get("triadic_lattice")]),
            "triad": "evidence + geometry + authority",
        },
        "boundary": "Recommendation arbitration may select a route. It may not execute it, grant authority, or skip final evolve before commit.",
    }
