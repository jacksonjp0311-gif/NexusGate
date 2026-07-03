from __future__ import annotations

from typing import Any

from nexus_gate.adapters.base import FrameworkAdapter
from nexus_gate.adapters.registry import AdapterManifest
from nexus_gate.core.packets import StatePacket


class LocalDemoAdapter(FrameworkAdapter):
    """Minimal local adapter proving the adapter -> StatePacket -> router path."""

    adapter_id = "local.demo"
    framework_name = "LocalDemo"
    framework_version = "0.1.7"

    def manifest(self) -> AdapterManifest:
        return AdapterManifest(
            adapter_id=self.adapter_id,
            framework_name=self.framework_name,
            adapter_version="0.1.7",
            supported_event_types=["demo.message", "demo.tool_request"],
            supported_action_classes=["read_only_signal", "tool_call"],
            supports_shadow=True,
            supports_trace_export=True,
            supports_replay=False,
            capability_bits=["normalize_event", "export_receptors", "shadow_supported", "trace_export"],
        )

    def detect_capabilities(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "framework_name": self.framework_name,
            "normalize_event": True,
            "export_receptors": True,
            "supports_shadow": True,
            "supports_trace_export": True,
            "supports_replay": False,
        }

    def normalize_event(self, raw_event: dict[str, Any]) -> StatePacket:
        event_type = str(raw_event.get("event_type", "demo.message"))
        requested_action = raw_event.get("requested_action", "read_only_signal")
        if requested_action not in {"read_only_signal", "tool_call"}:
            requested_action = "read_only_signal"

        return StatePacket(
            packet_id=str(raw_event.get("packet_id", "local-demo-packet")),
            source_framework=self.framework_name,
            source_surface=str(raw_event.get("source_surface", "local_demo")),
            schema_id=str(raw_event.get("schema_id", "NEXUS_STATE_PACKET")),
            schema_version=str(raw_event.get("schema_version", "0.1.7")),
            requested_action=requested_action,
            payload={
                "event_type": event_type,
                "message": raw_event.get("message", ""),
                "raw": raw_event,
            },
            provenance_chain=list(raw_event.get("provenance_chain", ["local.demo"])),
            profile_hash=raw_event.get("profile_hash"),
            origin_hash=raw_event.get("origin_hash"),
            authority_scope=list(raw_event.get("authority_scope", [])),
            metadata={"adapter_id": self.adapter_id, "adapter_version": "0.1.7"},
        )

    def export_receptors(self) -> list[dict[str, Any]]:
        return [
            {
                "receptor_id": "local.demo.readonly",
                "surface_type": "agent",
                "accepted_schema_families": ["NEXUS_STATE_PACKET"],
                "allowed_actions": ["read_only_signal"],
                "claim_boundary": "Local demo receptor is not production interoperability."
            }
        ]

    def supports_shadow(self) -> bool:
        return True
