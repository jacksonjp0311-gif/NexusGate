from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from assembly.telemetry.neuralforge_event_codec import utc_now


LAB_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = LAB_ROOT / "reports" / "neural_intelligence_distribution_latest.json"
HANDOFF_DIR = LAB_ROOT / "handoffs"

SUPPORTED_SURFACES = {
    "codex": {
        "surface_type": "repo_agent",
        "format": "bounded_patch_handoff",
        "priority": ["read_order", "evidence", "tests", "blocked_actions", "next_recommendation"],
    },
    "chatgpt": {
        "surface_type": "reasoning_chat",
        "format": "compressed_context_handoff",
        "priority": ["summary", "current_state", "uncertainties", "questions", "next_recommendation"],
    },
    "local_agent": {
        "surface_type": "local_agent",
        "format": "machine_json_handoff",
        "priority": ["schemas", "reports", "allowed_requests", "blocked_actions", "claim_boundary"],
    },
    "tui": {
        "surface_type": "operator_reflection",
        "format": "operator_summary",
        "priority": ["health", "recommendation", "blocked_actions", "report_paths"],
    },
    "electron": {
        "surface_type": "presentation_only",
        "format": "read_only_surface",
        "priority": ["status", "report_paths", "claim_boundary"],
    },
}

BLOCKED_ACTIONS = [
    "self_authorize",
    "auto_apply_fix",
    "arbitrary_shell",
    "external_api_write",
    "secret_access",
    "parent_repo_mutation",
    "bypass_evolve",
    "memory_promotion_without_evidence",
]

READ_ORDER = [
    "README.md",
    "AGENTS.md",
    "docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md",
    "docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md",
    "docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md",
    "labs/reflective_neural_assembly/MINI_README.md",
    "labs/reflective_neural_assembly/reports/neural_assembly_report_latest.json",
    "labs/reflective_neural_assembly/reports/neural_intelligence_distribution_latest.json",
]


def _compact(value: Any, limit: int = 900) -> str:
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    return text if len(text) <= limit else text[:limit] + "...[truncated]"


def build_distribution_packet(base_report: dict[str, Any], surfaces: list[str] | None = None) -> dict[str, Any]:
    selected = surfaces or list(SUPPORTED_SURFACES)
    unknown = [surface for surface in selected if surface not in SUPPORTED_SURFACES]
    if unknown:
        raise ValueError(f"unknown distribution surfaces: {', '.join(unknown)}")

    evidence = [
        "labs/reflective_neural_assembly/reports/neural_assembly_report_latest.json",
        "labs/reflective_neural_assembly/data/execution_events.jsonl",
        "state/ai_feedback_context_latest.json",
        "reports/nexus_reflective_loop_report_latest.json",
        "reports/nexus_domain_intelligence_report_latest.json",
    ]
    current_state = {
        "system": base_report.get("system", "NEXUS Reflective Neural Assembly"),
        "version": "0.5.1",
        "base_version": base_report.get("version", "unknown"),
        "status": base_report.get("status", "unknown"),
        "reasoning_mode": base_report.get("reasoning_mode", "analyze"),
        "recommendation": base_report.get("recommendation", ""),
        "confidence": base_report.get("confidence", 0.0),
        "uncertainty": base_report.get("uncertainty", []),
    }
    packets = {}
    for surface in selected:
        contract = SUPPORTED_SURFACES[surface]
        packets[surface] = {
            "surface": surface,
            "surface_type": contract["surface_type"],
            "handoff_format": contract["format"],
            "timestamp_utc": utc_now(),
            "compressed_context": _compact(current_state),
            "read_order": READ_ORDER,
            "evidence_references": evidence,
            "recommended_next_action": base_report.get("recommendation", "Continue observing."),
            "allowed_response": "recommend_only",
            "blocked_actions": BLOCKED_ACTIONS,
            "claim_boundary": "Distributed intelligence is compressed orientation evidence only, not authority.",
        }

    return {
        "system": "NEXUS Chat Intelligence Distribution",
        "version": "0.5.1",
        "status": "pass",
        "generated_at_utc": utc_now(),
        "source_report": "labs/reflective_neural_assembly/reports/neural_assembly_report_latest.json",
        "surfaces": selected,
        "surface_contracts": {surface: SUPPORTED_SURFACES[surface] for surface in selected},
        "packets": packets,
        "read_order": READ_ORDER,
        "write_surfaces": [
            "labs/reflective_neural_assembly/reports/neural_intelligence_distribution_latest.json",
            "labs/reflective_neural_assembly/handoffs/*.json",
            "labs/reflective_neural_assembly/handoffs/*.md",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": "Chat intelligence distribution optimizes rehydration for Codex, ChatGPT, local agents, TUI, and Electron. It does not self-authorize, execute shell, mutate the parent repo, write external APIs, access secrets, or bypass NEXUS gates.",
    }


def render_markdown_handoff(surface: str, packet: dict[str, Any]) -> str:
    lines = [
        f"# NEXUS Handoff: {surface}",
        "",
        f"Surface type: {packet['surface_type']}",
        f"Format: {packet['handoff_format']}",
        f"Generated: {packet['timestamp_utc']}",
        "",
        "## Recommended Next Action",
        packet["recommended_next_action"],
        "",
        "## Read Order",
    ]
    lines.extend(f"- {item}" for item in packet["read_order"])
    lines.extend(["", "## Evidence"])
    lines.extend(f"- {item}" for item in packet["evidence_references"])
    lines.extend(["", "## Blocked Actions"])
    lines.extend(f"- {item}" for item in packet["blocked_actions"])
    lines.extend(["", "## Claim Boundary", packet["claim_boundary"], ""])
    return "\n".join(lines)


def write_distribution(packet: dict[str, Any]) -> dict[str, str]:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    outputs = {"report": str(REPORT_PATH)}
    for surface, surface_packet in packet["packets"].items():
        json_path = HANDOFF_DIR / f"{surface}_handoff_latest.json"
        md_path = HANDOFF_DIR / f"{surface}_handoff_latest.md"
        json_path.write_text(json.dumps(surface_packet, indent=2), encoding="utf-8")
        md_path.write_text(render_markdown_handoff(surface, surface_packet), encoding="utf-8")
        outputs[f"{surface}_json"] = str(json_path)
        outputs[f"{surface}_markdown"] = str(md_path)
    return outputs

