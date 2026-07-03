from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.modes import RouteMode


@dataclass(frozen=True)
class RouteDecision:
    packet_id: str
    mode: RouteMode
    reason: str
    allowed_actions: list[str] = field(default_factory=list)
    denied_actions: list[str] = field(default_factory=list)
    registry_snapshot_hash: str | None = None
    policy_hash: str | None = None


class NexusRouter:
    """Low-latency hot-path router.

    Heavy scoring, replay, wound routing, demotion, and recalibration belong in
    the cold evidence plane. The hot path should stay deterministic and bounded.
    """

    def __init__(self, registry: dict[str, Any] | None = None) -> None:
        self.registry = registry or {}

    def route(self, packet: StatePacket) -> RouteDecision:
        if not packet.schema_id:
            return RouteDecision(
                packet_id=packet.packet_id,
                mode="reject",
                reason="schema_missing",
                denied_actions=[packet.requested_action],
            )

        if packet.requested_action in {
            "memory_write",
            "prompt_mutation",
            "api_call",
            "filesystem_write",
            "tool_call",
        }:
            if packet.requested_action not in packet.authority_scope:
                return RouteDecision(
                    packet_id=packet.packet_id,
                    mode="shadow",
                    reason="authority_unverified_shadow_only",
                    denied_actions=[packet.requested_action],
                )

        return RouteDecision(
            packet_id=packet.packet_id,
            mode="engage",
            reason="minimal_scaffold_gate_passed",
            allowed_actions=[packet.requested_action],
        )