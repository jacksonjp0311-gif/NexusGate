from __future__ import annotations

from typing import Any

from .workflow_analyzer import analyze_workflow


MODES = {"retry", "optimize", "predict", "pattern", "fix", "analyze"}


def decide(mode: str, context: dict[str, Any] | None = None, data: list[dict[str, Any]] | None = None, options: dict[str, Any] | None = None, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    mode = mode if mode in MODES else "analyze"
    events = history or data or []
    analysis = analyze_workflow(events)
    recommendation = "Continue governed observation."
    confidence = 0.55
    if mode in {"predict", "analyze", "pattern"}:
        recommendation = analysis["recommendations"][0]
        confidence = 0.65 if analysis["execution_count"] else 0.35
    if mode in {"fix", "retry", "optimize"}:
        recommendation = "Recommend a bounded diagnostic or optimization plan; require NEXUS gate and human authorization before execution."
        confidence = 0.6 if analysis["failure_rate"] else 0.45
    return {
        "mode": mode,
        "decision": "recommend",
        "recommendation": recommendation,
        "confidence": round(confidence, 3),
        "reasoning": [
            f"events={analysis['execution_count']}",
            f"failure_rate={analysis['failure_rate']}",
            f"duration_pattern={analysis['duration_pattern'].get('pattern')}",
        ],
        "analysis": analysis,
        "blocked_actions": ["auto_apply_fix", "arbitrary_shell", "external_api_write", "parent_repo_mutation", "self_authorize"],
        "claim_boundary": "Smart policy recommends only. It does not execute or authorize changes.",
    }
