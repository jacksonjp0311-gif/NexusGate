"""NEXUS GATE bounded NN model router.

This package routes reasoning packets to bounded local model roles and
handoff outputs. It does not grant authority to models and does not execute
model output.
"""

from .contract import VERSION, ROUTER_LAW, SAFETY_CONTRACT, ROLE_PREFERENCES, build_policy_manifest
from .detect import detect_ollama_inventory, assign_roles

__all__ = [
    "VERSION",
    "ROUTER_LAW",
    "SAFETY_CONTRACT",
    "ROLE_PREFERENCES",
    "build_policy_manifest",
    "detect_ollama_inventory",
    "assign_roles",
]