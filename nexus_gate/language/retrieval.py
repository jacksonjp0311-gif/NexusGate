from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import read_json

from .activation import activate
from .corpus import build_graph
from .intent import classify
from .tokenizer import char_ngrams, tokenize


def query(root: str | Path, text: str) -> dict[str, Any]:
    root_path = Path(root)
    graph, manifest = build_graph(root_path)
    seeds: dict[str, float] = {}
    for token in tokenize(text):
        node = f"lexical:{token.normalized}"
        if node in graph.nodes:
            seeds[node] = 1.0
    for gram in char_ngrams(text):
        node = f"lexical:{gram}"
        if node in graph.nodes:
            seeds[node] = max(seeds.get(node, 0.0), 0.25)
    intent = classify(text)
    activation = activate(graph, seeds) if seeds else {"activations": {}, "history": [], "iterations": 0, "converged": True}
    activated = [(node_id, value) for node_id, value in activation["activations"].items() if value > 0.05]
    concepts = [{"node_id": node, "label": graph.nodes[node].label, "score": round(score, 4)} for node, score in activated if graph.nodes[node].layer == "concept"][:10]
    entities = [{"node_id": node, "label": graph.nodes[node].label, "score": round(score, 4)} for node, score in activated if graph.nodes[node].layer in {"repository_entity", "procedural"}][:10]
    grounding = []
    for item in concepts + entities:
        grounding.extend(graph.nodes[item["node_id"]].evidence[:3])
    grounding = sorted(set(grounding))[:12]
    if intent["selected"] == "unknown_or_out_of_scope":
        answer = "NEXUS does not currently have verified evidence to answer that."
        grounding = []
        concepts = []
        entities = []
        uncertainty = {"level": "high", "reasons": ["no_supported_repository_domain_intent"]}
    else:
        command_hint = None
        if intent["selected"] == "inspect_learning":
            command_hint = "language-status"
            answer = "NEXUS language learning is evidence-gated. Verified interactions may teach; persistent conductance still requires repeated support and explicit human authorization."
        elif intent["selected"] == "inspect_conductance":
            command_hint = "conductance-field"
            answer = "NEXUS conductance can alter route preference, but authorization remains a non-adaptive gate."
        elif intent["selected"] == "ask_next_step":
            command_hint = "experience-readiness"
            answer = "The next permitted step should be chosen from current lifecycle evidence, usually by inspecting experience readiness or action status."
        else:
            answer = f"NEXUS classified this as {intent['selected']} and found repository-grounded evidence for the response."
        if command_hint:
            answer += f" The relevant bounded command is `{command_hint}`."
        uncertainty = {"level": "low" if grounding else "medium", "reasons": [] if grounding else ["limited_grounding"]}
    return {
        "schema": "NEXUS_LANGUAGE_QUERY.v2.9.0",
        "query_id": __import__("hashlib").sha256(text.encode()).hexdigest()[:24],
        "query_hash": __import__("hashlib").sha256(text.encode()).hexdigest(),
        "intent": intent,
        "activated_concepts": concepts,
        "activated_entities": entities,
        "evidence_paths": grounding,
        "contradictions": [],
        "response_plan": [{"claim": answer, "evidence": grounding}],
        "answer": answer,
        "grounding": grounding,
        "uncertainty": uncertainty,
        "activation_trace": activation["history"],
        "authority_boundary": {"recommendation_only": True, "may_execute": False, "may_authorize": False},
        "corpus_manifest_id": manifest["corpus_manifest_id"],
    }
