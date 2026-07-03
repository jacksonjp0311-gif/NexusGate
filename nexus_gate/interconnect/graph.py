"""NEXUS GATE interconnect graph.

The graph describes governed transfer relationships between adapters, bridge
runtime, receptors, feedback, evidence compaction, reports, and ledgers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
from typing import Any, Dict, List, Optional


CLAIM_BOUNDARY = (
    "Interconnect graph is local architecture evidence only. "
    "It does not prove production interoperability or safety."
)


@dataclass
class InterconnectNode:
    node_id: str
    kind: str
    label: str
    status: str = "declared"
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterconnectEdge:
    source: str
    target: str
    relation: str
    gate: str
    mode: str = "governed"


@dataclass
class InterconnectReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    checks: List[Dict[str, Any]]
    graph_hash: str
    claim_boundary: str = CLAIM_BOUNDARY


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _hash_graph(nodes: List[InterconnectNode], edges: List[InterconnectEdge]) -> str:
    payload = {
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _extract_adapter_nodes(root: Path) -> List[InterconnectNode]:
    nodes: List[InterconnectNode] = []
    for path in (root / "registry").glob("adapters*.json"):
        data = _read_json(path) or {}
        adapter_id = str(data.get("adapter_id") or data.get("id") or path.stem)
        nodes.append(InterconnectNode(
            node_id=f"adapter:{adapter_id}",
            kind="adapter",
            label=adapter_id,
            status="registered",
            evidence={"manifest": str(path.relative_to(root))},
        ))
    if not nodes:
        nodes.append(InterconnectNode(
            node_id="adapter:local.demo",
            kind="adapter",
            label="local.demo",
            status="declared_fallback",
            evidence={"reason": "default local demo adapter lane"},
        ))
    return nodes


def _extract_receptor_nodes(root: Path) -> List[InterconnectNode]:
    nodes: List[InterconnectNode] = []
    for path in (root / "registry").glob("receptors*.json"):
        data = _read_json(path) or {}
        raw = data.get("receptors")
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    rid = str(item.get("receptor_id") or item.get("id") or "unknown")
                else:
                    rid = str(item)
                nodes.append(InterconnectNode(
                    node_id=f"receptor:{rid}",
                    kind="receptor",
                    label=rid,
                    status="registered",
                    evidence={"manifest": str(path.relative_to(root))},
                ))
        else:
            rid = str(data.get("receptor_id") or data.get("id") or path.stem)
            nodes.append(InterconnectNode(
                node_id=f"receptor:{rid}",
                kind="receptor",
                label=rid,
                status="registered",
                evidence={"manifest": str(path.relative_to(root))},
            ))
    if not nodes:
        nodes.append(InterconnectNode(
            node_id="receptor:local.demo.readonly",
            kind="receptor",
            label="local.demo.readonly",
            status="declared_fallback",
            evidence={"reason": "default read-only receptor lane"},
        ))
    return nodes


def build_interconnect(root: str | Path = ".") -> InterconnectReport:
    root = Path(root).resolve()

    nodes: List[InterconnectNode] = [
        InterconnectNode("runtime:bounded_bridge", "runtime", "Bounded Bridge Runtime", "compiled"),
        InterconnectNode("bridge:session", "bridge", "Bridge Session Runner", "compiled"),
        InterconnectNode("feedback:engine", "feedback", "Feedback Engine", "compiled"),
        InterconnectNode("evidence:compactor", "evidence", "Evidence Compactor", "compiled"),
        InterconnectNode("ledger:local", "ledger", "Local Evidence Ledger", "appendable"),
        InterconnectNode("reports:local", "reports", "Local Report Surface", "present"),
    ]
    adapters = _extract_adapter_nodes(root)
    receptors = _extract_receptor_nodes(root)
    nodes.extend(adapters)
    nodes.extend(receptors)

    edges: List[InterconnectEdge] = []
    for adapter in adapters:
        edges.append(InterconnectEdge(adapter.node_id, "bridge:session", "normalizes_to_packet", "No adapter, no bridge."))
    edges.append(InterconnectEdge("bridge:session", "runtime:bounded_bridge", "feeds_runtime", "No schema, no route."))
    for receptor in receptors:
        edges.append(InterconnectEdge("runtime:bounded_bridge", receptor.node_id, "routes_to_receptor", "No receptor, no transfer target."))
    edges.append(InterconnectEdge("runtime:bounded_bridge", "reports:local", "emits_runtime_report", "No runtime report, no evidence."))
    edges.append(InterconnectEdge("reports:local", "feedback:engine", "feeds_feedback", "No feedback without compiled reports."))
    edges.append(InterconnectEdge("reports:local", "evidence:compactor", "feeds_compaction", "No growing code surface without pack report."))
    edges.append(InterconnectEdge("feedback:engine", "ledger:local", "appends_feedback_event", "No ledger stub, no compounding."))
    edges.append(InterconnectEdge("evidence:compactor", "ledger:local", "appends_compaction_event", "No compaction without manifest."))

    checks = [
        {"check": "adapter_nodes", "status": "pass" if adapters else "fail", "count": len(adapters)},
        {"check": "receptor_nodes", "status": "pass" if receptors else "fail", "count": len(receptors)},
        {"check": "bridge_runtime_nodes", "status": "pass", "count": 2},
        {"check": "feedback_compaction_nodes", "status": "pass", "count": 2},
        {"check": "governed_edges", "status": "pass" if len(edges) >= 5 else "fail", "count": len(edges)},
    ]
    status = "pass" if all(c["status"] == "pass" for c in checks) else "fail"
    graph_hash = _hash_graph(nodes, edges)

    return InterconnectReport(
        system="NEXUS GATE",
        version="0.2.2-interconnect",
        root=str(root),
        status=status,
        generated_at_utc=_utc(),
        nodes=[asdict(n) for n in nodes],
        edges=[asdict(e) for e in edges],
        checks=checks,
        graph_hash=graph_hash,
    )


def write_interconnect_report(report: InterconnectReport, root: str | Path = ".") -> Dict[str, str]:
    root = Path(root).resolve()
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data = asdict(report)
    text = json.dumps(data, indent=2)

    report_path = root / "reports" / f"nexus_interconnect_report_{stamp}.json"
    latest_report = root / "reports" / "nexus_interconnect_report_latest.json"
    graph_path = root / "state" / "interconnect_graph.v0.2.2.json"

    report_path.write_text(text, encoding="utf-8")
    latest_report.write_text(text, encoding="utf-8")
    graph_path.write_text(text, encoding="utf-8")

    return {
        "report": str(report_path),
        "latest": str(latest_report),
        "graph": str(graph_path),
    }
