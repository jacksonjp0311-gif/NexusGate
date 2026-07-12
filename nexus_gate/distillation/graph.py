from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.6.0"
SCHEMA = "NEXUS_EVIDENCE_DISTILLATION_GRAPH.v2.6.0"
REPORT_LATEST = Path("reports") / "nexus_evidence_distillation_report_latest.json"
STATE_LATEST = Path("state") / "distillation" / "nexus_evidence_graph_latest.json"
LEDGER = Path("ledger") / "evidence_distillation.jsonl"

CLAIM_BOUNDARY = (
    "Evidence Distillation Graph is local development compression evidence only. "
    "It preserves hashes, summaries, and graph links for heavy evidence surfaces. "
    "It does not prove correctness, safety, security, production readiness, "
    "scientific truth, model understanding, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "delete_source_files",
    "delete_docs_or_tests",
    "prune_without_distillation_node",
    "prune_without_source_hash",
    "self_authorize_pruning",
    "bypass_final_evolve",
    "external_api_writes",
    "secret_access",
]

SOURCE_PROTECTED_PREFIXES = (
    "nexus_gate/",
    "tests/",
    "docs/",
    "scripts/",
    "electron/",
    "Cortex/",
    "PetriDishPro/",
    "T3MP3ST/",
)

DISTILL_SURFACES = [
    "reports/nexus_origin_seal_latest.json",
    "reports/nexus_epoch_integrity_seal_latest.json",
    "reports/nexus_triadic_lattice_latest.json",
    "reports/nexus_decision_envelope_latest.json",
    "reports/nexus_coherence_field_latest.json",
    "reports/nexus_recommendation_outcome_latest.json",
    "reports/nexus_predictive_memory_orchestrator_latest.json",
    "reports/nexus_predictive_gate_timing_latest.json",
    "reports/nexus_runtime_hygiene_latest.json",
    "state/algorithms/nexus_algorithm_cards_latest.json",
    "state/discoveries/nexus_discovery_cards_latest.json",
    "state/latest_epoch_pointer.json",
    "state/lattice/nexus_triadic_lattice_latest.json",
    "state/coherence/arbiter_calibration_latest.json",
    "state/coherence/pressure_memory_latest.json",
]

BIOLOGICAL_PRINCIPLES = [
    {
        "principle_id": "efficient-coding",
        "summary": "Reduce predictable redundancy while preserving salient signal and provenance.",
        "nexus_translation": "Heavy evidence becomes compact graph nodes with source hashes.",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9298461/",
    },
    {
        "principle_id": "synaptic-pruning",
        "summary": "Repeatedly unused weak connections are candidates for pruning; used pathways strengthen.",
        "nexus_translation": "Old generated exhaust is prunable only after distillation; recurring useful nodes remain linked.",
        "source_url": "https://my.clevelandclinic.org/health/articles/synaptic-pruning",
    },
    {
        "principle_id": "small-world-efficiency",
        "summary": "High clustering plus short path length supports efficient global/local information flow.",
        "nexus_translation": "Distilled graph keeps local clusters and cross-surface bridge links for route analysis.",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5603984/",
    },
    {
        "principle_id": "homeostatic-retention",
        "summary": "Compression must preserve stability; pruning cannot outrun validation.",
        "nexus_translation": "Pruning remains recommendation-only until human authorization and final evolve.",
        "source_url": "https://elifesciences.org/reviewed-preprints/104746",
    },
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_obj(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _safe_rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _git(root: Path, args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=False, timeout=10)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _summarize_json(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"kind": type(data).__name__}
    selected = data.get("selected_action") or data.get("recommendation") or data.get("selected_next_action") or {}
    return {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "version": data.get("version") or data.get("product_version"),
        "mode": data.get("mode"),
        "score": (data.get("coherence") or {}).get("score") if isinstance(data.get("coherence"), dict) else None,
        "selected_command": selected.get("command") if isinstance(selected, dict) else None,
        "card_count": data.get("card_count"),
        "node_hint": data.get("system") or data.get("phase") or data.get("product_phase"),
    }


def _node_id(kind: str, source: str, digest: str) -> str:
    return f"{kind}:{hashlib.sha1((source + digest).encode('utf-8')).hexdigest()[:16]}"


def _evidence_node(root: Path, rel: str) -> dict[str, Any] | None:
    path = root / rel
    if not path.exists() or not path.is_file():
        return None
    data = path.read_bytes()
    digest = _sha_bytes(data)
    decoded = _read_json(path)
    summary = _summarize_json(decoded)
    kind = "EvidenceNode"
    if "algorithm_cards" in rel:
        kind = "AlgorithmNode"
    elif "discovery_cards" in rel:
        kind = "DiscoveryNode"
    elif "coherence" in rel:
        kind = "CoherenceNode"
    elif "decision" in rel:
        kind = "RouteNode"
    elif "outcome" in rel:
        kind = "OutcomeNode"
    elif "timing" in rel:
        kind = "RuntimePressureNode"
    return {
        "node_id": _node_id(kind, rel, digest),
        "node_type": kind,
        "summary": summary,
        "source_surface": rel,
        "source_hash": digest,
        "bytes": len(data),
        "confidence": 0.88 if decoded is not None else 0.55,
        "claim_boundary": "Distilled node is a compact pointer, not full context or proof.",
        "links": [],
        "prunable": False,
        "retention_policy": "keep_latest",
    }


def _biological_nodes() -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for item in BIOLOGICAL_PRINCIPLES:
        digest = _sha_obj(item)
        nodes.append({
            "node_id": _node_id("PrincipleNode", item["principle_id"], digest),
            "node_type": "PrincipleNode",
            "summary": item,
            "source_surface": item["source_url"],
            "source_hash": digest,
            "bytes": 0,
            "confidence": 0.72,
            "claim_boundary": "Biological principle is an engineering analogy, not biological proof.",
            "links": ["EvidenceNode", "RouteNode", "RuntimePressureNode"],
            "prunable": False,
            "retention_policy": "keep_raw_reference",
        })
    return nodes


def _runtime_exhaust_candidates(root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for folder in [root / "reports" / "human_surface", root / "reports" / "tmp"]:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            rel = _safe_rel(root, path)
            data = path.read_bytes()
            candidates.append({
                "path": rel,
                "bytes": len(data),
                "source_hash": _sha_bytes(data),
                "reason": "timestamped generated runtime exhaust",
                "protected": False,
            })
    return sorted(candidates, key=lambda item: item["bytes"], reverse=True)[:80]


def _protected_prune_candidate(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(SOURCE_PROTECTED_PREFIXES) or normalized in {"README.md", "AGENTS.md", "pyproject.toml"}


def _last_ledger_hash(path: Path) -> str:
    if not path.exists():
        return "genesis"
    for line in reversed(path.read_text(encoding="utf-8-sig").splitlines()):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        return item.get("event_hash") or "genesis"
    return "genesis"


def _append_ledger_event(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(event)
    body["previous_event_hash"] = _last_ledger_hash(path)
    body["event_id"] = _sha_obj({
        "graph_hash": body.get("graph_hash"),
        "previous_event_hash": body["previous_event_hash"],
        "generated_at_utc": body.get("generated_at_utc"),
    })
    body["event_hash"] = _sha_obj(body)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(body, sort_keys=True) + "\n")
        handle.flush()
    return body


def _pruning_plan(root: Path, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    raw = _runtime_exhaust_candidates(root)
    node_by_hash = {node.get("source_hash"): node for node in nodes if node.get("source_hash")}
    covered: list[dict[str, Any]] = []
    uncovered: list[dict[str, Any]] = []
    for item in raw:
        node = node_by_hash.get(item["source_hash"])
        if node and node.get("prunable") is True and not _protected_prune_candidate(item["path"]):
            covered.append({
                **item,
                "distillation_node_id": node.get("node_id"),
                "coverage": 1.0,
                "rehydration_test": "pending",
                "human_authorization_required": True,
            })
        else:
            uncovered.append({
                **item,
                "blocked_reason": "no prunable distillation node coverage",
            })
    blocked = [
        {"path": prefix, "reason": "source/docs/tests/policy surfaces are protected"}
        for prefix in ["nexus_gate/", "tests/", "docs/", "scripts/", "README.md", "AGENTS.md"]
    ]
    return {
        "mode": "recommendation_only",
        "candidate_count": len(covered),
        "candidate_bytes": sum(item["bytes"] for item in covered),
        "candidates": covered[:25],
        "uncovered_runtime_exhaust_count": len(uncovered),
        "uncovered_runtime_exhaust_bytes": sum(item["bytes"] for item in uncovered),
        "uncovered_runtime_exhaust_sample": uncovered[:25],
        "blocked_patterns": blocked,
        "requires_human_authorization": True,
        "requires_final_evolve": True,
        "apply_command_future": ".\\scripts\\nexus.ps1 prune-evidence",
    }


def _emergence_summary(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    for node in nodes:
        by_type[node["node_type"]] = by_type.get(node["node_type"], 0) + 1
    motif_count = sum(1 for node in nodes if node["node_type"] in {"RouteNode", "CoherenceNode", "OutcomeNode"})
    return {
        "status": "forming" if motif_count >= 3 else "insufficient_signal",
        "node_type_counts": by_type,
        "motif": "route + coherence + outcome" if motif_count >= 3 else None,
        "next_action": "Compare distillation graph across future evolve epochs to detect recurring motifs.",
    }


def build_evidence_distillation_graph(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    nodes = [node for rel in DISTILL_SURFACES if (node := _evidence_node(root_path, rel))]
    nodes.extend(_biological_nodes())
    edges = []
    node_ids = {node["source_surface"]: node["node_id"] for node in nodes}
    for source in [
        "reports/nexus_decision_envelope_latest.json",
        "reports/nexus_coherence_field_latest.json",
        "reports/nexus_recommendation_outcome_latest.json",
    ]:
        if source in node_ids:
            for target in ["state/algorithms/nexus_algorithm_cards_latest.json", "state/discoveries/nexus_discovery_cards_latest.json"]:
                if target in node_ids:
                    edges.append({"source": node_ids[source], "target": node_ids[target], "relation": "compressed_into_cards"})
    epoch_pointer = _read_json(root_path / "state" / "latest_epoch_pointer.json") or {}
    packet = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "phase": "Evidence Distillation Graph",
        "status": "pass" if len(nodes) >= 6 else "warn",
        "generated_at_utc": _utc(),
        "repository": {
            "commit": _git(root_path, ["rev-parse", "HEAD"]) or "unknown",
            "branch": _git(root_path, ["branch", "--show-current"]) or "unknown",
            "commit_role": "advisory; source_root epoch is primary when available",
        },
        "epoch_identity": {
            "epoch_id": epoch_pointer.get("epoch_id"),
            "source_root": epoch_pointer.get("source_root"),
            "epoch_state": epoch_pointer.get("epoch_state"),
            "pointer_boundary": epoch_pointer.get("pointer_boundary"),
        },
        "biological_efficiency_principles": BIOLOGICAL_PRINCIPLES,
        "nodes": nodes,
        "edges": edges,
        "graph_metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "distilled_source_bytes": sum(int(node.get("bytes") or 0) for node in nodes),
            "compression_mode": "summary_hash_pointer_graph",
        },
        "pruning_policy": _pruning_plan(root_path, nodes),
        "emergence": _emergence_summary(nodes),
        "read_surfaces": DISTILL_SURFACES,
        "write_surfaces": [REPORT_LATEST.as_posix(), STATE_LATEST.as_posix(), LEDGER.as_posix()],
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    packet["graph_hash"] = _sha_obj({"nodes": nodes, "edges": edges, "epoch_identity": packet["epoch_identity"]})
    return packet


def write_evidence_distillation_graph(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    packet = build_evidence_distillation_graph(root_path)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    for rel in (REPORT_LATEST, STATE_LATEST):
        path = root_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    ledger = root_path / LEDGER
    event = _append_ledger_event(ledger, {
        "schema": "NEXUS_EVIDENCE_DISTILLATION_LEDGER_EVENT.v2.6.1",
        "generated_at_utc": packet["generated_at_utc"],
        "graph_hash": packet["graph_hash"],
        "epoch_id": packet.get("epoch_identity", {}).get("epoch_id"),
        "source_root": packet.get("epoch_identity", {}).get("source_root"),
        "node_count": packet["graph_metrics"]["node_count"],
        "candidate_prune_bytes": packet["pruning_policy"]["candidate_bytes"],
        "uncovered_runtime_exhaust_bytes": packet["pruning_policy"]["uncovered_runtime_exhaust_bytes"],
    })
    packet["ledger_event_hash"] = event["event_hash"]
    for rel in (REPORT_LATEST, STATE_LATEST):
        path = root_path / rel
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS evidence distillation graph.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_evidence_distillation_graph(args.root)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        metrics = packet["graph_metrics"]
        print(f"NEXUS distillation graph: {packet['status']} nodes={metrics['node_count']} edges={metrics['edge_count']}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
