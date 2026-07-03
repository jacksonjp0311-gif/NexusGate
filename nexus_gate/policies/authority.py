from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AuthorityContract:
    """Declared authority boundary for a route surface."""

    contract_id: str
    allowed_actions: list[str] = field(default_factory=list)
    denied_actions: list[str] = field(default_factory=lambda: [
        "memory_write",
        "prompt_mutation",
        "provider_operation",
        "filesystem_write",
        "external_api_call",
        "spend_money",
        "delete_resource",
    ])

    def allows(self, action: str) -> bool:
        if action in self.denied_actions:
            return False
        return action in self.allowed_actions
