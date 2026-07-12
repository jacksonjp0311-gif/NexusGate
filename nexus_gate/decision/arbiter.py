from __future__ import annotations

from typing import Any


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
    score = int(((coherence.get("coherence") or {}).get("score")) or 0)
    entropy = int(((coherence.get("coherence") or {}).get("lineage_entropy")) or 0)
    source = recommendation.get("source")
    adjustment = 0
    if score and score < 70:
        if source in {"origin-seal", "coherence-field", "preflight"}:
            adjustment += 18
        if source == "final-seal":
            adjustment -= 20
    if entropy >= 8 and source in {"origin-seal", "coherence-field", "git-scope"}:
        adjustment += 8
    if ((coherence.get("coherence") or {}).get("missing_surfaces")) and source == "coherence-field":
        adjustment += 16
    return adjustment


def score_recommendation(recommendation: dict[str, Any], coherence: dict[str, Any] | None = None) -> dict[str, Any]:
    coherence = coherence or {}
    confidence = float(recommendation.get("confidence") or 0.0)
    severity = SEVERITY_WEIGHT.get(str(recommendation.get("severity", "info")), 10)
    source = SOURCE_PRIORITY.get(str(recommendation.get("source", "")), 8)
    cost = COST_PENALTY.get(str(recommendation.get("estimated_cost", "bounded")), 6)
    blockers = len(recommendation.get("blocking_conditions") or [])
    stale_penalty = 8 if recommendation.get("source_packet_hash") is None and recommendation.get("source") != "final-seal" else 0
    final_guard = 0
    if recommendation.get("source") == "final-seal":
        # Final evolve is mandatory before commit, but not usually the cheapest next routing action.
        final_guard = -18
    total = round(severity + source + (confidence * 20) + _coherence_adjustment(recommendation, coherence) - cost - blockers - stale_penalty + final_guard, 3)
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
        "final_guard": final_guard,
    }
    return scored


def arbitrate_recommendations(recommendations: list[dict[str, Any]], coherence: dict[str, Any] | None = None) -> dict[str, Any]:
    if not recommendations:
        raise ValueError("Cannot arbitrate an empty recommendation set.")
    scored = [score_recommendation(item, coherence) for item in recommendations]
    selected = sorted(scored, key=lambda item: item["arbiter_score"], reverse=True)[0]
    return {
        "schema": "NEXUS_RECOMMENDATION_ARBITER.v2.1.0",
        "mode": "causal_coherence_routing",
        "selected": selected,
        "scored_recommendations": scored,
        "coherence_input": {
            "status": (coherence or {}).get("status", "unknown"),
            "score": ((coherence or {}).get("coherence") or {}).get("score"),
            "lineage_entropy": ((coherence or {}).get("coherence") or {}).get("lineage_entropy"),
        },
        "boundary": "Recommendation arbitration may select a route. It may not execute it, grant authority, or skip final evolve before commit.",
    }
