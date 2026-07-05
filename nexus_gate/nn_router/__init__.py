"""NEXUS bounded NN model router."""

from .contract import (
    VERSION,
    ROUTER_LAW,
    SAFETY_CONTRACT,
    ROLE_PREFERENCES,
    build_policy_manifest,
    build_route_decision,
    choose_model,
    normalize_target_role,
    selected_roles,
)

__all__ = [
    "VERSION",
    "ROUTER_LAW",
    "SAFETY_CONTRACT",
    "ROLE_PREFERENCES",
    "build_policy_manifest",
    "build_route_decision",
    "choose_model",
    "normalize_target_role",
    "selected_roles",
]

