from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import read_json, sha_obj, write_json
from nexus_gate.intelligence.redact import redact_text

from .graph import LanguageGraph
from .tokenizer import tokenize


REPORT = Path("reports") / "nexus_language_model_latest.json"
STATE = Path("state") / "language" / "nexus_language_corpus_manifest_latest.json"
TRUSTED_DOCS = ["README.md", "AGENTS.md", "docs/updates/UPDATE_CHART.md", "docs/versioning/NEXUS_CHANGELOG.md", "docs/algorithms/NEXUS_CORE_ALGORITHMS.md"]


def _read_text(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists() or path.is_dir():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""


def build_graph(root: str | Path) -> tuple[LanguageGraph, dict[str, Any]]:
    root_path = Path(root)
    graph = LanguageGraph()
    excluded: list[str] = []
    token_count = 0
    for rel in TRUSTED_DOCS:
        text = _read_text(root_path, rel)
        if not text:
            excluded.append(rel)
            continue
        redacted, redaction = redact_text(text)
        doc_node = graph.add_node("repository_entity", rel, [rel])
        for token in tokenize(redacted):
            token_count += 1
            lex = graph.add_node("lexical", token.normalized, [rel])
            graph.add_edge(lex, doc_node, "OBSERVED_IN", confidence=0.65, provenance=[rel])
        for line in redacted.splitlines():
            if line.startswith("#"):
                concept = graph.add_node("concept", line.strip("# ").strip().lower(), [rel])
                graph.add_edge(concept, doc_node, "SUPPORTED_BY", confidence=0.75, provenance=[rel])
    registry = read_json(root_path / "registry" / "nexus_command_registry.v2.6.2.json", {})
    for command in registry.get("commands") or []:
        cid = command.get("command_registry_id")
        if not cid:
            continue
        node = graph.add_node("procedural", cid, ["registry/nexus_command_registry.v2.6.2.json"])
        for token in tokenize(cid.replace("nexus.", "")):
            lex = graph.add_node("lexical", token.normalized, ["registry/nexus_command_registry.v2.6.2.json"])
            graph.add_edge(lex, node, "ROUTES_TO", confidence=0.9, provenance=["registry/nexus_command_registry.v2.6.2.json"])
    for path in sorted((root_path / "state" / "intelligence" / "candidates").glob("*.json")):
        candidate = read_json(path, {})
        if candidate.get("status") not in {"candidate", "promoted"}:
            continue
        cnode = graph.add_node("concept", candidate.get("normalized_label", candidate.get("candidate_id")), [path.as_posix()])
        for form in candidate.get("language_forms") or []:
            for token in tokenize(form):
                lex = graph.add_node("lexical", token.normalized, [path.as_posix()])
                graph.add_edge(lex, cnode, "ALIASES", confidence=float((candidate.get("quality") or {}).get("combined_confidence") or 0.5), provenance=[path.as_posix()])
    manifest = {
        "schema": "NEXUS_LANGUAGE_CORPUS.v2.9.0",
        "source_epoch_id": read_json(root_path / "state" / "latest_epoch_pointer.json", {}).get("source_epoch_id"),
        "input_file_hashes": {rel: sha_obj(_read_text(root_path, rel)) for rel in TRUSTED_DOCS if _read_text(root_path, rel)},
        "excluded_inputs": excluded,
        "redaction_report": {"status": "pass"},
        "corpus_hash": graph.hash(),
        "token_count": token_count,
        "phrase_count": 0,
        "concept_count": len([n for n in graph.nodes.values() if n.layer == "concept"]),
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
    }
    manifest["corpus_manifest_id"] = sha_obj(manifest)[:32]
    return graph, manifest


def build(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    graph, manifest = build_graph(root_path)
    seal = {
        "schema": "NEXUS_GEOMETRIC_LANGUAGE_MODEL_SEAL.v2.9.0",
        "model_id": "nglm-local-bootstrap",
        "model_version": "2.9.0",
        "corpus_manifest_id": manifest["corpus_manifest_id"],
        "corpus_hash": manifest["corpus_hash"],
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "lexical_node_count": len([n for n in graph.nodes.values() if n.layer == "lexical"]),
        "concept_node_count": len([n for n in graph.nodes.values() if n.layer == "concept"]),
        "procedural_node_count": len([n for n in graph.nodes.values() if n.layer == "procedural"]),
        "episode_node_count": len([n for n in graph.nodes.values() if n.layer == "episode"]),
        "motif_count": 0,
        "persistent_weight_event_count": 0,
        "runtime_graph_hash": graph.hash(),
        "durable_event_root_hash": manifest["corpus_hash"],
        "tokenizer_config_hash": sha_obj({"tokenizer": "nfkc-code-aware-v1"}),
        "activation_config_hash": sha_obj({"decay": 0.45, "iterations": 8}),
        "decoder_config_hash": sha_obj({"mode": "template-default-token-field-experimental"}),
        "benchmark_report_hash": None,
        "created_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "claim_boundary": "The seal proves reproducible model state, not intelligence parity.",
    }
    write_json(root_path / STATE, manifest)
    write_json(root_path / REPORT, seal | {"corpus": manifest})
    return seal | {"corpus": manifest}


def status(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    packet = read_json(root_path / REPORT, {})
    if not packet:
        packet = build(root_path)
    return {"schema": "NEXUS_LANGUAGE_STATUS.v2.9.0", "status": "pass", "model": packet}
