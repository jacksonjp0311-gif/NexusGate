from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.core.packets import StatePacket
from nexus_gate.receptors.compatibility import CompatibilityDecision, evaluate_compatibility
from nexus_gate.receptors.registry import ReceptorManifest, load_receptor_manifests
from nexus_gate.runtime.router import NexusRouter


def safe_model_dict(value: Any) -> dict[str, Any]:
    """Serialize simple dataclass/model objects without assuming to_dict exists."""

    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return value.model_dump()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {"repr": repr(value)}


@dataclass(frozen=True)
class BridgeSessionReport:
    system: str
    version: str
    session_id: str
    generated_at_utc: str
    packet_id: str
    adapter_id: str
    receptor_id: str | None
    route_mode: str
    route_reason: str
    compatibility_mode: str
    compatibility_reason: str
    final_mode: str
    final_reason: str
    packet: dict[str, Any]
    compatibility: dict[str, Any] | None
    claim_boundary: str = "BridgeSessionReport is local bridge evidence only. Not production interoperability."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BridgeSessionRunner:
    """Bounded local bridge runner.

    Flow:
    raw event -> adapter -> StatePacket -> router -> receptor compatibility -> final decision.
    """

    def __init__(self, receptor_manifest_path: str | Path = "registry/receptors.local_demo.v0.1.8.json") -> None:
        self.adapter = LocalDemoAdapter()
        self.router = NexusRouter()
        self.receptor_manifest_path = Path(receptor_manifest_path)
        self.receptors = load_receptor_manifests(self.receptor_manifest_path)

    def select_receptor(self, packet: StatePacket) -> ReceptorManifest | None:
        compatible_schema = [
            receptor
            for receptor in self.receptors
            if packet.schema_id in receptor.accepted_schema_families
        ]
        action_matches = [
            receptor
            for receptor in compatible_schema
            if packet.requested_action in receptor.allowed_actions
        ]
        if action_matches:
            return action_matches[0]
        if compatible_schema:
            return compatible_schema[0]
        return None

    @staticmethod
    def combine_modes(route_mode: str, compatibility_mode: str) -> tuple[str, str]:
        if route_mode == "reject" or compatibility_mode == "reject":
            return "reject", "route_or_compatibility_rejected"
        if route_mode == "shadow" or compatibility_mode == "shadow":
            return "shadow", "route_or_compatibility_requires_shadow"
        if route_mode == "engage" and compatibility_mode == "compatible":
            return "engage", "route_and_receptor_compatible"
        if route_mode == "abstain":
            return "abstain", "router_abstained"
        return "defer", "bridge_not_ready"

    def run(self, raw_event: dict[str, Any]) -> BridgeSessionReport:
        packet = self.adapter.normalize_event(raw_event)
        route = self.router.route(packet)
        receptor = self.select_receptor(packet)

        compatibility: CompatibilityDecision | None = None
        compatibility_mode = "reject"
        compatibility_reason = "no_receptor"

        if receptor is not None:
            compatibility = evaluate_compatibility(packet, receptor)
            compatibility_mode = compatibility.mode
            compatibility_reason = compatibility.reason

        final_mode, final_reason = self.combine_modes(route.mode, compatibility_mode)

        return BridgeSessionReport(
            system="NEXUS GATE",
            version="0.1.9b-bridge-session",
            session_id=str(raw_event.get("session_id", "local-demo-session")),
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            packet_id=packet.packet_id,
            adapter_id=self.adapter.adapter_id,
            receptor_id=receptor.receptor_id if receptor else None,
            route_mode=route.mode,
            route_reason=route.reason,
            compatibility_mode=compatibility_mode,
            compatibility_reason=compatibility_reason,
            final_mode=final_mode,
            final_reason=final_reason,
            packet=safe_model_dict(packet),
            compatibility=compatibility.to_dict() if compatibility else None,
        )

    def run_json(self, raw_event: dict[str, Any]) -> str:
        return json.dumps(self.run(raw_event).to_dict(), indent=2)
