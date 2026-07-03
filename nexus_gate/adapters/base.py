from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from nexus_gate.core.packets import StatePacket


class FrameworkAdapter(ABC):
    """Base adapter contract.

    Runtime law:
    No adapter, no bridge.
    """

    adapter_id: str
    framework_name: str
    framework_version: str | None = None

    @abstractmethod
    def detect_capabilities(self) -> dict[str, Any]:
        """Return framework capabilities as a stable map."""

    @abstractmethod
    def normalize_event(self, raw_event: dict[str, Any]) -> StatePacket:
        """Convert a raw framework event into a canonical StatePacket."""

    @abstractmethod
    def export_receptors(self) -> list[dict[str, Any]]:
        """Return receptor manifests exposed by this adapter."""

    def supports_shadow(self) -> bool:
        return False
