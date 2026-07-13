from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from nexus_gate.breath.pulse import build_breath_packet
from nexus_gate.field.conductance import build_conductance_field
from nexus_gate.intelligence.common import read_json
from nexus_gate.language.retrieval import query as language_query
from nexus_gate.language.self_model import build as build_self_model

from .messages import create_message
from .state import latest_epoch


def damped_diffusion(
    nodes: list[str],
    edges: list[tuple[str, str, float]],
    seeds: dict[str, float],
    *,
    damping: float = 0.82,
    maximum_iterations: int = 20,
    convergence_tolerance: float = 1e-6,
    contradiction: dict[str, float] | None = None,
    uncertainty: dict[str, float] | None = None,
) -> dict[str, Any]:
    node_set = list(dict.fromkeys(nodes))
    outgoing: dict[str, list[tuple[str, float]]] = defaultdict(list)
    totals: dict[str, float] = defaultdict(float)
    for source, target, weight in edges:
        if weight < 0:
            raise ValueError("conductance_must_be_nonnegative")
        outgoing[source].append((target, float(weight)))
        totals[source] += float(weight)
    seed = {node: max(0.0, min(1.0, float(seeds.get(node, 0.0)))) for node in node_set}
    current = dict(seed)
    residuals: list[float] = []
    history: list[dict[str, float]] = []
    for _ in range(maximum_iterations):
        nxt = {node: (1.0 - damping) * seed.get(node, 0.0) for node in node_set}
        for source in node_set:
            total = totals.get(source, 0.0)
            if total <= 0:
                continue
            for target, weight in outgoing.get(source, []):
                nxt[target] = nxt.get(target, 0.0) + damping * (weight / total) * current.get(source, 0.0)
        for node, pressure in (contradiction or {}).items():
            nxt[node] = max(0.0, nxt.get(node, 0.0) - pressure)
        for node, pressure in (uncertainty or {}).items():
            nxt[node] = max(0.0, nxt.get(node, 0.0) - pressure)
        residual = sum(abs(nxt.get(node, 0.0) - current.get(node, 0.0)) for node in node_set)
        residuals.append(round(residual, 10))
        current = {node: max(0.0, min(1.0, value)) for node, value in nxt.items()}
        history.append(dict(sorted(current.items(), key=lambda item: (-item[1], item[0]))[:12]))
        if residual < convergence_tolerance:
            break
    return {
        "iterations": len(residuals),
        "converged": bool(residuals and residuals[-1] < convergence_tolerance),
        "residual": residuals[-1] if residuals else 0.0,
        "residuals": residuals,
        "activations": dict(sorted(current.items(), key=lambda item: (-item[1], item[0]))),
        "top_activated_nodes": [{"node_id": node, "score": round(score, 6)} for node, score in sorted(current.items(), key=lambda item: (-item[1], item[0]))[:10]],
        "history": history,
        "contraction_error_bound_after_20": round(damping**20, 6),
    }


def build_inner_context(root: str | Path, prompt: str, cycle_id: str) -> dict[str, Any]:
    root_path = Path(root)
    epoch = latest_epoch(root_path)
    breath = build_breath_packet(root_path)
    conductance = build_conductance_field(root_path, prompt)
    language = language_query(root_path, prompt)
    self_model = build_self_model(root_path)
    messages = [
        create_message(cycle_id=cycle_id, topic="identity.current", message_type="state_observation", source_organ="identity", target_organs=["language", "authority_boundary"], source_epoch_id=epoch["source_epoch_id"], payload=epoch, quality={"provenance": 1, "verification": 0.9, "freshness": 0.9, "confidence": 0.9}),
        create_message(cycle_id=cycle_id, topic="breath.pressure", message_type="state_observation", source_organ="breath", target_organs=["conductance", "language"], source_epoch_id=epoch["source_epoch_id"], payload={"vitality": breath.get("vitality"), "pressure": breath.get("pressure"), "phase": breath.get("breath", {}).get("phase")}, quality={"provenance": 1, "verification": 0.8, "freshness": 0.8, "confidence": 0.8}),
        create_message(cycle_id=cycle_id, topic="conductance.field", message_type="route_preference", source_organ="conductance", target_organs=["language"], source_epoch_id=epoch["source_epoch_id"], payload=conductance.get("route_recommendation", {}), quality={"provenance": 1, "verification": 0.8, "freshness": 0.8, "confidence": 0.75}),
        create_message(cycle_id=cycle_id, topic="language.intent", message_type="activation_result", source_organ="language", target_organs=["self_model", "authority_boundary"], source_epoch_id=epoch["source_epoch_id"], payload={"intent": language.get("intent"), "grounding": language.get("grounding")}, quality={"provenance": 1, "verification": 0.75, "freshness": 0.75, "confidence": 0.75}),
        create_message(cycle_id=cycle_id, topic="self_model.capability", message_type="state_observation", source_organ="self_model", target_organs=["language", "authority_boundary"], source_epoch_id=epoch["source_epoch_id"], payload={"capabilities": self_model.get("capabilities"), "blocked_claims": self_model.get("blocked_claims")}, quality={"provenance": 1, "verification": 0.85, "freshness": 0.75, "confidence": 0.8}),
        create_message(cycle_id=cycle_id, topic="authority.required", message_type="authority_boundary", source_organ="authority_boundary", target_organs=["language"], source_epoch_id=epoch["source_epoch_id"], payload={"may_execute": False, "may_authorize": False, "may_mutate_source": False, "recommendation_only": True}, quality={"provenance": 1, "verification": 1, "freshness": 1, "confidence": 1}, authority_class="blocked"),
    ]
    nodes = ["prompt", "identity", "breath", "conductance", "language", "self_model", "authority"]
    edges = [
        ("prompt", "language", 1.0),
        ("identity", "language", 0.8),
        ("breath", "conductance", 0.6),
        ("conductance", "language", 0.7),
        ("language", "self_model", 0.7),
        ("self_model", "authority", 1.0),
    ]
    activation = damped_diffusion(nodes, edges, {"prompt": 1.0, "identity": 0.7, "breath": 0.4})
    return {"epoch": epoch, "breath": breath, "conductance": conductance, "language": language, "self_model": self_model, "messages": messages, "activation": activation}
