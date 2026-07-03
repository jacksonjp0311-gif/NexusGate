"""NEXUS GATE interconnect graph.

The graph describes governed transfer relationships between adapters, bridge
runtime, receptors, feedback, evidence compaction, reports, ledgers, operator
surfaces, and AI-agent handoff processes.
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
    "It does not prove production interoperability, safety, consciousness, "
    "autonomous authority, or correctness."
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


def _path_status(root: Path, relative: str) -> Dict[str, Any]:
    path = root / relative
    return {
        "path": relative,
        "exists": path.exists(),
    }


def _ai_process_nodes(root: Path) -> List[InterconnectNode]:
    """Declare local AI/operator process surfaces without granting authority."""

    return [
        InterconnectNode(
            "operator:tui",
            "operator_surface",
            "PowerShell HUD TUI",
            "declared",
            _path_status(root, "scripts/nexus_tui.ps1"),
        ),
        InterconnectNode(
            "operator:ui_alias",
            "operator_surface",
            "PowerShell UI Compatibility Alias",
            "declared",
            _path_status(root, "scripts/nexus_ui.ps1"),
        ),
        InterconnectNode(
            "ai_agent:codex_process",
            "ai_agent_process",
            "Codex/ChatGPT Handoff Process",
            "bounded_handoff",
            {
                "authority": "recommendation_only",
                "writes": "human_authorized_patch_only",
                "external_api_writes": False,
            },
        ),
        InterconnectNode(
            "feedback:ai_context",
            "feedback_surface",
            "AI Feedback Context",
            "present",
            _path_status(root, "state/ai_feedback_context_latest.json"),
        ),
        InterconnectNode(
            "feedback:markdown_log",
            "feedback_surface",
            "Feedback Log",
            "present",
            _path_status(root, "docs/feedback/FEEDBACK_LOG.md"),
        ),
        InterconnectNode(
            "feedback:operator_packets",
            "operation_packet_surface",
            "Operator Packet Directory",
            "declared",
            _path_status(root, "docs/feedback/operator_packets"),
        ),
        InterconnectNode(
            "reports:tui_exports",
            "report_surface",
            "TUI AI Handoff and Snapshot Exports",
            "declared",
            {
                "handoff": _path_status(root, "reports/tui/nexus_tui_ai_handoff_latest.txt"),
                "snapshot": _path_status(root, "reports/tui/nexus_tui_snapshot_latest.html"),
            },
        ),
    ]


def _domain_interconnect_nodes(root: Path) -> List[InterconnectNode]:
    """Declare domain profiles as routing contracts, not scientific validation."""

    return [
        InterconnectNode(
            "terminal:cli_format",
            "operator_format",
            "CLI Formatting Profile",
            "declared",
            {
                "patterns": ["colored output", "progress indicator", "bounded table rows", "plain text fallback"],
                "evidence": [
                    "PowerShell Write-Host ForegroundColor/BackgroundColor",
                    "PowerShell Write-Progress status bar",
                ],
            },
        ),
        InterconnectNode(
            "domain:bio",
            "domain_profile",
            "Biological Data Interconnection Profile",
            "declared",
            {
                "identifiers": ["BioProject", "BioSample", "SRA Study", "SRA Experiment", "SRA Run"],
                "gate": "No biological claim without source metadata and validation evidence.",
            },
        ),
        InterconnectNode(
            "domain:chem",
            "domain_profile",
            "Chemical Data Interconnection Profile",
            "declared",
            {
                "identifiers": ["InChI", "InChIKey", "SMILES"],
                "gate": "No chemical claim without structure identifier and provenance.",
            },
        ),
        InterconnectNode(
            "domain:coding",
            "domain_profile",
            "Coding Tool Interconnection Profile",
            "declared",
            {
                "formats": ["LSP", "SARIF", "OpenAPI", "JSON Schema"],
                "gate": "No code-tool route without machine-readable contract or diagnostics evidence.",
            },
        ),
        InterconnectNode(
            "domain:neural",
            "domain_profile",
            "Neural Model Interconnection Profile",
            "declared",
            {
                "formats": ["ONNX graph", "operator set", "model metadata"],
                "gate": "No neural route without model format, runtime boundary, and evidence report.",
            },
        ),
        InterconnectNode(
            "schema:domain_interop_profile",
            "schema",
            "Domain Interoperability Profile Schema",
            "declared",
            _path_status(root, "state/domain_interconnection_index.v0.2.7.json"),
        ),
    ]


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
    ai_nodes = _ai_process_nodes(root)
    domain_nodes = _domain_interconnect_nodes(root)
    nodes.extend(adapters)
    nodes.extend(receptors)
    nodes.extend(ai_nodes)
    nodes.extend(domain_nodes)

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
    edges.append(InterconnectEdge("feedback:engine", "feedback:ai_context", "emits_ai_context", "No AI handoff without feedback context."))
    edges.append(InterconnectEdge("feedback:engine", "feedback:markdown_log", "appends_feedback_log", "No AI handoff without feedback log."))
    edges.append(InterconnectEdge("feedback:ai_context", "ai_agent:codex_process", "hydrates_agent_process", "Hydration before mutation."))
    edges.append(InterconnectEdge("feedback:markdown_log", "ai_agent:codex_process", "hydrates_agent_history", "No patch without update visibility."))
    edges.append(InterconnectEdge("ai_agent:codex_process", "feedback:operator_packets", "proposes_operation_packet", "No autonomous self-authorization."))
    edges.append(InterconnectEdge("operator:tui", "feedback:operator_packets", "writes_bounded_packet", "No UI bypass of compiler/evolve gates."))
    edges.append(InterconnectEdge("operator:tui", "reports:tui_exports", "exports_ai_handoff", "No external API writes."))
    edges.append(InterconnectEdge("operator:ui_alias", "operator:tui", "routes_to_terminal_tui", "The UI must never own the logic."))
    edges.append(InterconnectEdge("reports:tui_exports", "ai_agent:codex_process", "rehydrates_this_process", "Certificate before compounding."))
    edges.append(InterconnectEdge("ai_agent:codex_process", "operator:tui", "returns_recommendation_to_operator", "Human-authorized patch applies mutation."))
    edges.append(InterconnectEdge("operator:tui", "terminal:cli_format", "renders_governed_status", "No operator flood."))
    edges.append(InterconnectEdge("terminal:cli_format", "reports:local", "summarizes_evidence_surface", "No raw JSON wall unless requested."))
    for domain in ["domain:bio", "domain:chem", "domain:coding", "domain:neural"]:
        edges.append(InterconnectEdge("ai_agent:codex_process", domain, "requests_domain_route", "Domain routing is not domain validation."))
        edges.append(InterconnectEdge(domain, "schema:domain_interop_profile", "binds_domain_contract", "No schema, no route."))
        edges.append(InterconnectEdge("schema:domain_interop_profile", "bridge:session", "normalizes_domain_packet", "No normalized StatePacket, no route."))
        edges.append(InterconnectEdge(domain, "reports:local", "emits_domain_evidence", "No evidence, no compounding."))

    checks = [
        {"check": "adapter_nodes", "status": "pass" if adapters else "fail", "count": len(adapters)},
        {"check": "receptor_nodes", "status": "pass" if receptors else "fail", "count": len(receptors)},
        {"check": "bridge_runtime_nodes", "status": "pass", "count": 2},
        {"check": "feedback_compaction_nodes", "status": "pass", "count": 2},
        {"check": "ai_process_nodes", "status": "pass" if len(ai_nodes) >= 5 else "fail", "count": len(ai_nodes)},
        {
            "check": "ai_agent_governed_edges",
            "status": "pass" if any(e.target == "ai_agent:codex_process" for e in edges) else "fail",
            "count": len([e for e in edges if e.source == "ai_agent:codex_process" or e.target == "ai_agent:codex_process"]),
        },
        {"check": "domain_interconnect_nodes", "status": "pass" if len(domain_nodes) >= 6 else "fail", "count": len(domain_nodes)},
        {
            "check": "domain_interconnect_edges",
            "status": "pass" if all(any(e.source == d or e.target == d for e in edges) for d in ["domain:bio", "domain:chem", "domain:coding", "domain:neural"]) else "fail",
            "count": len([e for e in edges if e.source.startswith("domain:") or e.target.startswith("domain:")]),
        },
        {"check": "governed_edges", "status": "pass" if len(edges) >= 5 else "fail", "count": len(edges)},
    ]
    status = "pass" if all(c["status"] == "pass" for c in checks) else "fail"
    graph_hash = _hash_graph(nodes, edges)

    return InterconnectReport(
        system="NEXUS GATE",
        version="0.2.7-domain-interconnect",
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
