from __future__ import annotations

from typing import Any

from .graph import LanguageGraph


RELATION_GAIN = {
    "ALIASES": 0.9,
    "ROUTES_TO": 0.85,
    "SUPPORTED_BY": 0.7,
    "OBSERVED_IN": 0.45,
    "CONTRADICTS": -0.8,
}


def activate(graph: LanguageGraph, seeds: dict[str, float], iterations: int = 8, decay: float = 0.45) -> dict[str, Any]:
    current = {node: max(0.0, min(1.0, value)) for node, value in seeds.items() if node in graph.nodes}
    history: list[dict[str, float]] = []
    for _ in range(iterations):
        nxt = {node: min(1.0, value * decay) for node, value in current.items()}
        for node, value in current.items():
            for edge_id in graph.outgoing.get(node, []):
                edge = graph.edges[edge_id]
                gain = RELATION_GAIN.get(edge.relation, 0.35)
                if gain < 0:
                    nxt[edge.target] = max(0.0, nxt.get(edge.target, 0.0) + gain * value * edge.confidence)
                else:
                    nxt[edge.target] = min(1.0, nxt.get(edge.target, 0.0) + value * gain * edge.confidence * min(1.0, edge.conductance))
        history.append({key: round(nxt[key], 6) for key in sorted(nxt, key=nxt.get, reverse=True)[:12]})
        delta = sum(abs(nxt.get(key, 0.0) - current.get(key, 0.0)) for key in set(nxt) | set(current))
        current = nxt
        if delta < 0.0001:
            break
    ranked = sorted(current.items(), key=lambda item: (-item[1], item[0]))
    return {"activations": dict(ranked), "history": history, "iterations": len(history), "converged": len(history) < iterations}
