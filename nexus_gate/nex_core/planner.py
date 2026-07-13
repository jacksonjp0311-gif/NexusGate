from __future__ import annotations

from typing import Any


def build_response_plan(language_packet: dict[str, Any], inner_context: dict[str, Any]) -> list[dict[str, Any]]:
    answer = language_packet.get("answer") or "NEX does not currently have verified evidence to answer that."
    grounding = list(language_packet.get("grounding") or language_packet.get("evidence_paths") or [])
    if not grounding and "does not currently have verified evidence" not in answer:
        answer = "NEX does not currently have verified evidence to answer that."
    return [
        {
            "claim": answer,
            "evidence": grounding,
            "authority_boundary": "recommendation_only",
        }
    ]


def compose_grounded_response(plan: list[dict[str, Any]]) -> dict[str, Any]:
    blocked: list[str] = []
    parts: list[str] = []
    grounding: list[str] = []
    for item in plan:
        claim = str(item.get("claim") or "").strip()
        evidence = list(item.get("evidence") or [])
        if claim and not evidence and "does not currently have verified evidence" not in claim:
            blocked.append(claim)
            continue
        if claim:
            parts.append(claim)
            grounding.extend(evidence)
    if not parts:
        parts = ["NEX does not currently have verified evidence to answer that."]
    return {"answer": "\n".join(parts), "grounding": sorted(set(grounding)), "blocked_claims": blocked}
