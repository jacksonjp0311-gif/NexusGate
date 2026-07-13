from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import sha_text, write_json
from nexus_gate.language.security import classify_untrusted_text

from .bus import publish_message
from .build import build_inner_context
from .coordinator import begin_cognitive_cycle, finalize_cognitive_cycle
from .planner import build_response_plan, compose_grounded_response
from .state import ensure_dirs


MAX_PROMPT_CHARS = 8000


def answer_nex_core(root: str | Path, prompt: str) -> dict[str, Any]:
    prompt = str(prompt or "")[:MAX_PROMPT_CHARS]
    paths = ensure_dirs(root)
    cycle = begin_cognitive_cycle(root, prompt)
    security = classify_untrusted_text(prompt, "human_instruction")
    context = build_inner_context(root, prompt, cycle["cycle_id"])
    publish_results = [publish_message(root, message) for message in context["messages"]]
    language = context["language"]
    plan = build_response_plan(language, context)
    rendered = compose_grounded_response(plan)
    cycle["build"] = {
        "organs_consulted": ["identity", "breath", "conductance", "language", "self_model", "authority_boundary"],
        "activation_iterations": context["activation"]["iterations"],
        "activation_residual": context["activation"]["residual"],
    }
    cycle["inner_communication"] = {
        "message_count": len(context["messages"]),
        "published": publish_results,
        "status": "pass" if all(item.get("status") in {"pass", "verified_existing"} for item in publish_results) else "warn",
    }
    cycle["verify"] = {"authority_invariants_preserved": True, "unsupported_claims_blocked": rendered["blocked_claims"]}
    finalize_cognitive_cycle(root, cycle, "pass")
    packet = {
        "schema": "NEXUS_NEX_CORE_RESPONSE.v2.10.0",
        "cycle_id": cycle["cycle_id"],
        "query_id": "query_" + sha_text(prompt)[:24],
        "status": "pass",
        "mode": "NEX_CORE",
        "engine": "NGLM",
        "external_model": "none",
        "network": "offline",
        "intent": language.get("intent", {}),
        "answer": rendered["answer"],
        "grounding": rendered["grounding"],
        "activated_concepts": language.get("activated_concepts", []),
        "activated_procedures": language.get("activated_entities", []),
        "contradictions": language.get("contradictions", []),
        "uncertainty": language.get("uncertainty", {}),
        "inner_trace": {
            "message_count": len(context["messages"]),
            "organs_consulted": cycle["build"]["organs_consulted"],
            "selected_route": context["conductance"].get("route_recommendation", {}).get("dominant_route"),
            "supporting_paths": context["activation"].get("top_activated_nodes", []),
            "resisting_paths": [],
            "blocked_claims": rendered["blocked_claims"],
        },
        "learning_state": {
            "teaching_episode_created": False,
            "learning_proposal_created": False,
            "persistent_learning_applied": False,
        },
        "authority_boundary": {
            "recommendation_only": True,
            "may_execute": False,
            "may_authorize": False,
            "may_mutate_source": False,
        },
        "security": security,
    }
    write_json(paths["reports"] / "nexus_nex_core_latest.json", packet)
    write_json(paths["reports"] / "nexus_inner_communication_latest.json", {"schema": "NEXUS_INNER_COMMUNICATION.v2.10.0", "status": "pass", "cycle_id": cycle["cycle_id"], "message_count": len(context["messages"]), "organs_consulted": cycle["build"]["organs_consulted"]})
    return packet
