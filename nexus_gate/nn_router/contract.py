"""Policy contract for the NEXUS bounded NN model router v0.6.4.

The router distributes intelligence, not authority. It prepares bounded
recommendations and handoff packets. It does not execute tool calls, mutate
files from model output, read secrets, or write external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Mapping, Optional


VERSION = "0.6.4"

VALID_TARGET_ROLES: List[str] = ["ALL", "FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"]

ROUTER_LAW: List[str] = [
    "No adapter, no bridge.",
    "No schema, no route.",
    "No codec, no transfer.",
    "No authority, no mutation.",
    "No replay evidence, no memory promotion.",
    "No evidence ledger, no compounding.",
    "Distribute intelligence, not authority.",
    "No model output may directly execute tools or mutate files.",
]

SAFETY_CONTRACT: Dict[str, bool] = {
    "recommendation_only": True,
    "model_grants_authority": False,
    "model_output_executes_tools": False,
    "model_output_mutates_files": False,
    "arbitrary_shell_allowed": False,
    "secrets_access_allowed": False,
    "external_api_writes_allowed": False,
    "local_ollama_api_allowed_only_when_requested": True,
    "human_authorizes_durable_mutation": True,
    "role_targeting_required_for_deep_calls": True,
}

ROLE_PREFERENCES: Dict[str, List[str]] = {
    "FAST": ["phi3:mini", "phi3:latest"],
    "BALANCED": ["phi3:mini", "phi3:latest"],
    "DEEP": ["mistral:latest"],
    "TNN": [],
    "HANDOFF": [],
}

ROLE_DESCRIPTIONS: Dict[str, str] = {
    "FAST": "Quick local recommendation voice using Phi-3 when available.",
    "BALANCED": "Balanced local recommendation voice using Phi-3 when available.",
    "DEEP": "Deeper local recommendation voice using Mistral when available.",
    "TNN": "Tesseract Neural Network minimal governed NN surface.",
    "HANDOFF": "No local model required; writes ChatGPT/Codex handoff packets.",
}

ALLOWED_ROUTE_KINDS: List[str] = [
    "inventory",
    "health",
    "recommendation",
    "handoff",
    "drift_scorecard",
]

BLOCKED_CAPABILITIES: List[str] = [
    "arbitrary_shell",
    "direct_tool_execution",
    "file_mutation_from_model_output",
    "secret_access",
    "external_api_write",
    "authority_claim",
    "memory_promotion_without_replay_evidence",
    "compounding_without_evidence_ledger",
]


@dataclass(frozen=True)
class RoleAssignment:
    role: str
    model: Optional[str]
    available: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RouteDecision:
    intent: str
    route_kind: str
    role: str
    model: Optional[str]
    call_model: bool
    model_called: bool
    recommendation_only: bool
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def normalize_target_role(role: str | None) -> str:
    normalized = (role or "ALL").upper().strip()
    if normalized not in VALID_TARGET_ROLES:
        raise ValueError(f"Unsupported NEXUS NN role: {role}")
    return normalized


def selected_roles(target_role: str | None) -> List[str]:
    normalized = normalize_target_role(target_role)
    if normalized == "ALL":
        return ["FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"]
    return [normalized]


def choose_model(available_models: Mapping[str, object], role: str) -> RoleAssignment:
    """Select a model for a role from an inventory mapping.

    This only chooses a recommendation lane. It does not call the model and
    does not authorize any action.
    """
    normalized_role = role.upper()
    if normalized_role == "TNN":
        return RoleAssignment(
            role="TNN",
            model="Tesseract Neural Network/minimal-receipt-surface",
            available=True,
            reason="TNN reads minimal NeuralForge governance receipts through NexusGate.",
        )

    if normalized_role == "HANDOFF":
        return RoleAssignment(
            role="HANDOFF",
            model=None,
            available=True,
            reason="HANDOFF writes packets and requires no local model.",
        )

    preferences = ROLE_PREFERENCES.get(normalized_role, [])
    for preferred in preferences:
        if preferred in available_models:
            return RoleAssignment(
                role=normalized_role,
                model=preferred,
                available=True,
                reason=f"Selected preferred local model {preferred}.",
            )

    return RoleAssignment(
        role=normalized_role,
        model=None,
        available=False,
        reason=f"No preferred local model found for role {normalized_role}.",
    )


def build_policy_manifest() -> Dict[str, object]:
    return {
        "version": VERSION,
        "router_law": list(ROUTER_LAW),
        "safety_contract": dict(SAFETY_CONTRACT),
        "role_preferences": {key: list(value) for key, value in ROLE_PREFERENCES.items()},
        "role_descriptions": dict(ROLE_DESCRIPTIONS),
        "valid_target_roles": list(VALID_TARGET_ROLES),
        "allowed_route_kinds": list(ALLOWED_ROUTE_KINDS),
        "blocked_capabilities": list(BLOCKED_CAPABILITIES),
        "authority_boundary": {
            "models": "recommendation_only",
            "tools": "gated_by_nexus",
            "durable_mutation": "human_authorized",
            "handoffs": "compressed_context_only",
            "deep_reasoning": "role_targeted_mistral_recommendation_only",
        },
    }


def build_route_decision(
    intent: str,
    role: str,
    inventory: Mapping[str, object],
    call_model: bool = False,
    route_kind: str = "recommendation",
) -> RouteDecision:
    assignment = choose_model(inventory, role)
    will_call = bool(call_model and assignment.available and assignment.model)
    return RouteDecision(
        intent=intent,
        route_kind=route_kind,
        role=assignment.role,
        model=assignment.model,
        call_model=bool(call_model),
        model_called=will_call,
        recommendation_only=True,
        reason=assignment.reason,
    )
