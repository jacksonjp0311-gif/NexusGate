"""NEXUS GATE — Governed Agentic Transfer Layer."""

__version__ = "0.1.0"

from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.router import NexusRouter, RouteDecision

__all__ = [
    "__version__",
    "StatePacket",
    "NexusRouter",
    "RouteDecision",
]