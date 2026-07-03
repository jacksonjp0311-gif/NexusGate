from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


RouteIntent = Literal[
    "read_only_signal",
    "warning_signal",
    "tool_call",
    "memory_write",
    "prompt_mutation",
    "api_call",
    "filesystem_write",
]


@dataclass(frozen=True)
class StatePacket:
    """Canonical packet passed through NEXUS GATE.

    The router should never process raw framework events directly.
    Every framework event must be normalized through a FrameworkAdapter first.
    """

    packet_id: str
    source_framework: str
    source_surface: str
    schema_id: str
    schema_version: str
    requested_action: RouteIntent
    payload: dict[str, Any]
    provenance_chain: list[str] = field(default_factory=list)
    profile_hash: str | None = None
    origin_hash: str | None = None
    authority_scope: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)