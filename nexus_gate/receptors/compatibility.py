from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from nexus_gate.core.packets import StatePacket
from nexus_gate.receptors.registry import ReceptorManifest


@dataclass(frozen=True)
class CompatibilityDecision:
    receptor_id: str
    mode: str
    reason: str
    schema_supported: bool
    action_supported: bool
    authority_required: bool
    authority_present: bool
    claim_boundary: str = "CompatibilityDecision is local routing evidence only."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_compatibility(packet: StatePacket, receptor: ReceptorManifest) -> CompatibilityDecision:
    schema_supported = packet.schema_id in receptor.accepted_schema_families
    action_supported = packet.requested_action in receptor.allowed_actions
    authority_required = packet.requested_action in receptor.requires_authority_for_actions
    authority_present = bool(packet.authority_scope)

    if not schema_supported:
        return CompatibilityDecision(receptor.receptor_id, "reject", "unsupported_schema", False, action_supported, authority_required, authority_present)
    if not action_supported:
        return CompatibilityDecision(receptor.receptor_id, "reject", "unsupported_action", True, False, authority_required, authority_present)
    if authority_required and not authority_present:
        return CompatibilityDecision(receptor.receptor_id, "shadow", "authority_required_missing", True, True, True, False)
    return CompatibilityDecision(receptor.receptor_id, "compatible", "schema_action_authority_compatible", True, True, authority_required, authority_present)
