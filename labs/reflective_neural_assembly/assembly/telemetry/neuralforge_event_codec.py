from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


BLOCKED_ADAPTER_ACTIONS = [
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "secret_exfiltration",
    "credential_storage",
    "unbounded_crawling",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate(value: Any, limit: int = 500) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[:limit] + "...[truncated]"


@dataclass
class ParentEmitterPacket:
    source_platform: str
    source_model: str
    session_id: str
    timestamp_utc: str
    user_intent: str
    reasoning_summary: str
    proposed_actions: list[str] = field(default_factory=list)
    evidence_references: list[str] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    raw_text: str = ""

    def validate(self) -> dict[str, Any]:
        missing = [
            name
            for name in ["source_platform", "source_model", "session_id", "timestamp_utc", "user_intent"]
            if not getattr(self, name)
        ]
        blocked = "self_authorize" in [item.lower() for item in self.proposed_actions]
        return {
            "valid": not missing and not blocked,
            "missing": missing,
            "blocked_action_requested": blocked,
            "claim_boundary": "Parent emitter packets are reasoning evidence only, not authority.",
        }


def make_parent_emitter_packet(intent: str, raw_text: str = "", source_model: str = "unknown") -> ParentEmitterPacket:
    return ParentEmitterPacket(
        source_platform="nexus_reflective_neural_assembly",
        source_model=source_model,
        session_id=f"rna-{uuid4()}",
        timestamp_utc=utc_now(),
        user_intent=intent,
        reasoning_summary=_truncate(raw_text or intent),
        proposed_actions=[],
        evidence_references=[],
        uncertainties=["lab output is recommendation-only"],
        boundaries=[
            "no self-authorization",
            "no arbitrary shell",
            "no external API writes",
            "no parent repo mutation",
        ],
        raw_text=_truncate(raw_text, 2000),
    )


def telemetry_adapter_contract() -> dict[str, Any]:
    return {
        "local_file": {"enabled": True, "mode": "read_write_lab_only"},
        "http_readonly": {"enabled": False},
        "github_readonly": {"enabled": False},
        "api_checkpoint": {"enabled": False},
        "blocked": BLOCKED_ADAPTER_ACTIONS,
        "claim_boundary": "Telemetry adapters are disabled by default except local lab files. No external writes.",
    }


def normalize_event(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    status = str(raw.get("status") or ("success" if raw.get("success") is True else "unknown")).lower()
    success = bool(raw.get("success")) if "success" in raw else status in {"success", "passed", "ok", "pass"}
    event = {
        "workflow_id": str(raw.get("workflow_id") or raw.get("id") or f"wf-{uuid4()}"),
        "workflow_name": str(raw.get("workflow_name") or raw.get("name") or "unknown_workflow"),
        "tool_name": str(raw.get("tool_name") or raw.get("tool") or raw.get("action") or "unknown_tool"),
        "action": str(raw.get("action") or raw.get("tool_name") or "unknown_action"),
        "status": status,
        "success": success,
        "duration_ms": float(raw.get("duration_ms") or raw.get("duration") or 0.0),
        "step_count": int(raw.get("step_count") or raw.get("steps") or 0),
        "retry_count": int(raw.get("retry_count") or raw.get("retries") or 0),
        "error_type": str(raw.get("error_type") or ""),
        "recovery_action": str(raw.get("recovery_action") or ""),
        "params": raw.get("params") if isinstance(raw.get("params"), dict) else {},
        "prompt": _truncate(raw.get("prompt") or raw.get("input")),
        "response": _truncate(raw.get("response") or raw.get("output")),
        "timestamp": str(raw.get("timestamp") or raw.get("timestamp_utc") or utc_now()),
    }
    return event


def append_event(path: str | Path, event: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalize_event(event), sort_keys=True) + "\n")


def load_events(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(normalize_event(json.loads(line)))
    return events


def packet_to_dict(packet: ParentEmitterPacket) -> dict[str, Any]:
    data = asdict(packet)
    data["validation"] = packet.validate()
    return data
