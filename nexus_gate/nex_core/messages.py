from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus_gate.intelligence.common import sha_obj, utc


ALLOWED_AUTHORITY_CLASSES = {"evidence_only", "recommendation_only", "authority_required", "blocked"}
ALLOWED_ORGANS = {
    "identity",
    "source_epoch",
    "breath",
    "telemetry",
    "conductance",
    "language",
    "self_model",
    "ai_touch",
    "teaching",
    "experience",
    "action_lifecycle",
    "algorithm_memory",
    "discovery_memory",
    "contradiction",
    "verification",
    "authority_boundary",
}


def message_reliability(quality: dict[str, Any]) -> float:
    p = float(quality.get("provenance", 0.0))
    v = float(quality.get("verification", 0.0))
    f = float(quality.get("freshness", 0.0))
    c = float(quality.get("confidence", 0.0))
    return round(max(0.0, min(1.0, p * v * f * c)), 6)


def create_message(
    *,
    cycle_id: str,
    topic: str,
    message_type: str,
    source_organ: str,
    target_organs: list[str],
    source_epoch_id: str,
    payload: dict[str, Any],
    quality: dict[str, Any] | None = None,
    causal_refs: list[str] | None = None,
    authority_class: str = "evidence_only",
    hop_count: int = 0,
    hop_limit: int = 8,
    previous_message_hash: str = "genesis",
) -> dict[str, Any]:
    quality = dict(quality or {"provenance": 1.0, "verification": 0.75, "freshness": 0.75, "confidence": 0.75})
    quality["combined_reliability"] = message_reliability(quality)
    body = {
        "schema": "NEXUS_INNER_MESSAGE.v2.10.0",
        "message_id": "",
        "cycle_id": cycle_id,
        "topic": topic,
        "message_type": message_type,
        "source_organ": source_organ,
        "target_organs": target_organs,
        "created_at_utc": utc(),
        "source_epoch_id": source_epoch_id,
        "payload": payload,
        "payload_hash": sha_obj(payload),
        "quality": quality,
        "causal_refs": causal_refs or [],
        "authority_class": authority_class,
        "hop_count": hop_count,
        "hop_limit": hop_limit,
        "previous_message_hash": previous_message_hash,
    }
    body["message_id"] = "msg_" + sha_obj({k: v for k, v in body.items() if k != "message_id"})[:24]
    body["message_hash"] = sha_obj({k: v for k, v in body.items() if k != "message_hash"})
    return body


def validate_message(message: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if message.get("schema") != "NEXUS_INNER_MESSAGE.v2.10.0":
        errors.append("schema_mismatch")
    if message.get("authority_class") not in ALLOWED_AUTHORITY_CLASSES:
        errors.append("invalid_authority_class")
    if message.get("source_organ") not in ALLOWED_ORGANS:
        errors.append("unknown_source_organ")
    if message.get("source_organ") in set(message.get("target_organs") or []):
        errors.append("immediate_source_to_self_reflection")
    if int(message.get("hop_count") or 0) > int(message.get("hop_limit") or 0):
        errors.append("hop_limit_exceeded")
    expected_payload_hash = sha_obj(message.get("payload") or {})
    if message.get("payload_hash") != expected_payload_hash:
        errors.append("payload_hash_mismatch")
    expected_hash = sha_obj({k: v for k, v in message.items() if k != "message_hash"})
    if message.get("message_hash") != expected_hash:
        errors.append("message_hash_mismatch")
    return {"valid": not errors, "errors": errors, "message_hash": expected_hash}
