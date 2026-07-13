from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus_gate.intelligence.common import sha_obj


@dataclass
class Node:
    node_id: str
    layer: str
    label: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class Edge:
    edge_id: str
    source: str
    target: str
    relation: str
    conductance: float = 1.0
    confidence: float = 0.5
    support_count: int = 1
    contradiction_count: int = 0
    provenance: list[str] = field(default_factory=list)
    persistent: bool = False
    authority_classification: str = "preference_only"


class LanguageGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.outgoing: dict[str, list[str]] = {}

    def add_node(self, layer: str, label: str, evidence: list[str] | None = None) -> str:
        node_id = f"{layer}:{label.lower()}"
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, layer, label, evidence or [])
        else:
            self.nodes[node_id].evidence = sorted(set(self.nodes[node_id].evidence + (evidence or [])))
        return node_id

    def add_edge(self, source: str, target: str, relation: str, *, conductance: float = 1.0, confidence: float = 0.5, provenance: list[str] | None = None, persistent: bool = False) -> str:
        edge_id = sha_obj({"source": source, "target": target, "relation": relation})[:32]
        self.edges[edge_id] = Edge(edge_id, source, target, relation, max(0.01, min(10.0, conductance)), max(0.0, min(1.0, confidence)), provenance=provenance or [], persistent=persistent)
        self.outgoing.setdefault(source, []).append(edge_id)
        return edge_id

    def hash(self) -> str:
        return sha_obj(
            {
                "nodes": {key: self.nodes[key].__dict__ for key in sorted(self.nodes)},
                "edges": {key: self.edges[key].__dict__ for key in sorted(self.edges)},
            }
        )

    def to_packet(self) -> dict[str, Any]:
        return {
            "nodes": [self.nodes[key].__dict__ for key in sorted(self.nodes)],
            "edges": [self.edges[key].__dict__ for key in sorted(self.edges)],
            "graph_hash": self.hash(),
        }
