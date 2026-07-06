from __future__ import annotations

from typing import Dict, List

VERSION = "0.8.8"


def evaluate_authority(
    lane_policy: Dict[str, object],
    capability_policy: Dict[str, object],
    human_authorized: bool = False,
    execute_requested: bool = False,
) -> Dict[str, object]:
    reasons: List[str] = []

    if not lane_policy.get("known"):
        reasons.append("unknown_lane")
    if not lane_policy.get("allowed"):
        reasons.append("lane_not_allowed")
    if not capability_policy.get("allowed"):
        reasons.append("forbidden_capability_active")
    if execute_requested and not human_authorized:
        reasons.append("execution_requires_human_authorization")

    may_build_packet = lane_policy.get("known") is True and lane_policy.get("allowed") is True
    may_execute = (
        may_build_packet
        and capability_policy.get("allowed") is True
        and human_authorized is True
        and execute_requested is True
    )

    return {
        "version": VERSION,
        "may_build_packet": bool(may_build_packet),
        "may_execute_controlled_lane": bool(may_execute),
        "human_authorized": bool(human_authorized),
        "execute_requested": bool(execute_requested),
        "decision": "allow_controlled_execution" if may_execute else ("packet_only" if may_build_packet else "deny"),
        "reasons": reasons,
        "boundary": "Authority applies only to controlled internal lanes. It is not arbitrary shell authority.",
    }
