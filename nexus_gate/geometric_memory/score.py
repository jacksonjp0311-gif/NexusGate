"""Small deterministic score helpers for geometry packets."""

from __future__ import annotations

from typing import Dict, Mapping


AXES = ("Intent", "Evidence", "Authority", "Context")


def axis_complete(axis_status: Mapping[str, bool]) -> float:
    return sum(1 for axis in AXES if axis_status.get(axis, False)) / float(len(AXES))


def build_gate_flags(axis_status: Mapping[str, bool], authority: str) -> Dict[str, bool]:
    authority_text = (authority or "").strip().lower()
    read_only = authority_text in {"", "read_only", "readonly", "recommendation_only"}
    human_authorized = authority_text in {"human_authorized", "approved", "y", "yes"}

    return {
        "intent_ok": bool(axis_status.get("Intent")),
        "evidence_ok": bool(axis_status.get("Evidence")),
        "authority_ok": bool(axis_status.get("Authority")),
        "context_ok": bool(axis_status.get("Context")),
        "read_only": read_only,
        "human_authorized": human_authorized,
    }
