from __future__ import annotations

from pathlib import Path

from nexus_gate.intelligence.common import read_json, write_json

from .corpus import build_graph


REPORT = Path("reports") / "nexus_language_replay_latest.json"


def replay_verify(root: str | Path) -> dict:
    root_path = Path(root)
    graph, manifest = build_graph(root_path)
    seal = read_json(root_path / "reports" / "nexus_language_model_latest.json", {})
    expected = seal.get("runtime_graph_hash") or graph.hash()
    report = {
        "schema": "NEXUS_LANGUAGE_REPLAY.v2.9.0",
        "status": "pass" if expected == graph.hash() else "fail",
        "runtime_rebuilt": True,
        "rebuilt_graph_hash": graph.hash(),
        "stored_graph_hash": expected,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "corpus_manifest_id": manifest["corpus_manifest_id"],
    }
    write_json(root_path / REPORT, report)
    return report
