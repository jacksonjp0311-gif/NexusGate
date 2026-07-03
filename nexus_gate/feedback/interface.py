"""AI-readable feedback interface for NEXUS GATE.

This module exposes the feedback state in two surfaces:

1. `state/ai_feedback_context_latest.json` for AI agents and Codex-like systems.
2. `docs/feedback/FEEDBACK_LOG.md` for a human-readable append-only log.

It does not execute repairs or mutate target runtime surfaces beyond writing
feedback/interface evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
from typing import Any, Dict, List, Optional


CLAIM_BOUNDARY = (
    "AI feedback interface is a local repository orientation surface. "
    "It does not prove correctness, security, safety, production readiness, or autonomous repair authority."
)


@dataclass
class AIFeedbackInterfaceReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    ai_context_path: str
    markdown_log_path: str
    health_score: float
    evidence_pressure: str
    dominant_pressure_source: str
    next_action: str
    two_way_commands: List[str]
    latest_report_paths: Dict[str, str]
    log_entry_hash: str
    claim_boundary: str = CLAIM_BOUNDARY


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "unreadable", "error": str(exc), "path": str(path)}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_get(data: Optional[Dict[str, Any]], path: List[str], default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def compile_ai_feedback_context(root: str | Path = ".") -> Dict[str, Any]:
    root = Path(root).resolve()
    reports = {
        "feedback": root / "reports" / "nexus_feedback_report_latest.json",
        "self_healing": root / "reports" / "nexus_self_healing_report_latest.json",
        "interconnect": root / "reports" / "nexus_interconnect_report_latest.json",
        "evidence_compaction": root / "reports" / "nexus_evidence_compaction_report_latest.json",
        "runtime": root / "reports" / "nexus_runtime_compile_report_latest.json",
        "pack": root / "dist" / "nexus_gate_pack_manifest_latest.json",
    }

    feedback = _read_json(reports["feedback"])
    healing = _read_json(reports["self_healing"])
    interconnect = _read_json(reports["interconnect"])
    compaction = _read_json(reports["evidence_compaction"])

    context = {
        "system": "NEXUS GATE",
        "version": "0.2.3-ai-feedback-interface",
        "generated_at_utc": _utc(),
        "status": "pass",
        "repo_role": "governed agentic transfer boundary",
        "human_commands": {
            "evolve": ".\\scripts\\nexus.ps1 evolve",
            "heal": ".\\scripts\\nexus.ps1 heal",
            "feedback": ".\\scripts\\nexus.ps1 feedback",
            "interface": ".\\scripts\\nexus.ps1 interface",
            "status": ".\\scripts\\nexus.ps1 status",
        },
        "ai_read_surfaces": {
            "feedback_log": "docs/feedback/FEEDBACK_LOG.md",
            "feedback_system": "docs/feedback/FEEDBACK_SYSTEM.md",
            "ai_context": "state/ai_feedback_context_latest.json",
            "latest_feedback_report": "reports/nexus_feedback_report_latest.json",
            "latest_self_healing_report": "reports/nexus_self_healing_report_latest.json",
            "latest_interconnect_report": "reports/nexus_interconnect_report_latest.json",
            "latest_evidence_compaction_report": "reports/nexus_evidence_compaction_report_latest.json",
        },
        "two_way_protocol": [
            "AI reads state/ai_feedback_context_latest.json first.",
            "AI reads docs/feedback/FEEDBACK_LOG.md for recent evolution history.",
            "AI proposes typed recommendation, not direct mutation.",
            "Human-authorized patch performs mutation.",
            "Patch runs .\\scripts\\nexus.ps1 evolve.",
            "Feedback interface appends the new result to FEEDBACK_LOG.md.",
        ],
        "health": {
            "health_score": _safe_get(feedback, ["health_score"], 0.0),
            "feedback_status": _safe_get(feedback, ["status"], "missing"),
            "evidence_pressure": _safe_get(feedback, ["evidence_pressure", "pressure_level"], _safe_get(compaction, ["pressure_level"], "unknown")),
            "dominant_pressure_source": _safe_get(healing, ["dominant_pressure_source"], "unknown"),
            "self_healing_status": _safe_get(healing, ["status"], "missing"),
            "interconnect_status": _safe_get(interconnect, ["status"], "missing"),
            "node_count": len(_safe_get(interconnect, ["nodes"], [])),
            "edge_count": len(_safe_get(interconnect, ["edges"], [])),
        },
        "next_action": _safe_get(healing, ["next_action"], _safe_get(feedback, ["next_actions"], ["Run .\\scripts\\nexus.ps1 evolve"])[0] if isinstance(_safe_get(feedback, ["next_actions"], []), list) and _safe_get(feedback, ["next_actions"], []) else "Run .\\scripts\\nexus.ps1 evolve"),
        "latest_report_paths": {k: str(v.relative_to(root)) for k, v in reports.items()},
        "claim_boundary": CLAIM_BOUNDARY,
    }

    return context


def _markdown_log_entry(context: Dict[str, Any]) -> str:
    health = context.get("health", {})
    lines = [
        f"## {context.get('generated_at_utc', _utc())} - NEXUS Feedback Interface",
        "",
        f"- status: `{context.get('status', 'unknown')}`",
        f"- health score: `{health.get('health_score', 0.0)}`",
        f"- evidence pressure: `{health.get('evidence_pressure', 'unknown')}`",
        f"- self-healing status: `{health.get('self_healing_status', 'unknown')}`",
        f"- dominant pressure source: `{health.get('dominant_pressure_source', 'unknown')}`",
        f"- interconnect: `{health.get('node_count', 0)} nodes / {health.get('edge_count', 0)} edges`",
        f"- next action: `{context.get('next_action', '')}`",
        "",
        "### AI Handoff",
        "",
        "```text",
        "Read state/ai_feedback_context_latest.json first.",
        "Then read this log for recent feedback history.",
        "Propose a typed recommendation; do not assume autonomous write authority.",
        "Human-authorized patches must run .\\scripts\\nexus.ps1 evolve.",
        "```",
        "",
        "### Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def write_ai_feedback_interface(root: str | Path = ".") -> AIFeedbackInterfaceReport:
    root = Path(root).resolve()
    context = compile_ai_feedback_context(root)

    state_dir = root / "state"
    docs_dir = root / "docs" / "feedback"
    reports_dir = root / "reports"
    state_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    context_path = state_dir / "ai_feedback_context_latest.json"
    log_path = docs_dir / "FEEDBACK_LOG.md"
    system_path = docs_dir / "FEEDBACK_SYSTEM.md"

    context_text = json.dumps(context, indent=2)
    context_path.write_text(context_text, encoding="utf-8")

    if not system_path.exists():
        system_path.write_text(
            "# NEXUS GATE Feedback System\n\n"
            "This folder is the canonical feedback interface for future AI systems.\n\n"
            "Read order:\n\n"
            "1. `state/ai_feedback_context_latest.json`\n"
            "2. `docs/feedback/FEEDBACK_LOG.md`\n"
            "3. `reports/nexus_feedback_report_latest.json`\n"
            "4. `reports/nexus_self_healing_report_latest.json`\n\n"
            "Hard law: no autonomous mutation from feedback. Feedback becomes typed recommendation, dry-run plan, human-authorized apply gate, validation evidence, then log entry.\n",
            encoding="utf-8",
        )

    entry = _markdown_log_entry(context)
    if not log_path.exists():
        log_path.write_text("# NEXUS GATE Feedback Log\n\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as f:
        f.write("\n" + entry)

    report = AIFeedbackInterfaceReport(
        system="NEXUS GATE",
        version="0.2.3-ai-feedback-interface",
        root=str(root),
        status="pass",
        generated_at_utc=context["generated_at_utc"],
        ai_context_path=str(context_path.relative_to(root)),
        markdown_log_path=str(log_path.relative_to(root)),
        health_score=float(context["health"].get("health_score", 0.0) or 0.0),
        evidence_pressure=str(context["health"].get("evidence_pressure", "unknown")),
        dominant_pressure_source=str(context["health"].get("dominant_pressure_source", "unknown")),
        next_action=str(context.get("next_action", "")),
        two_way_commands=list(context["human_commands"].values()),
        latest_report_paths=context["latest_report_paths"],
        log_entry_hash=_hash(entry),
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data = asdict(report)
    report_text = json.dumps(data, indent=2)
    (reports_dir / f"nexus_feedback_interface_report_{stamp}.json").write_text(report_text, encoding="utf-8")
    (reports_dir / "nexus_feedback_interface_report_latest.json").write_text(report_text, encoding="utf-8")
    return report
