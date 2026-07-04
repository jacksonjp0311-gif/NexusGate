from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DomainCard:
    card_type: str
    domain: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    claim_boundary: str = "Card is local study evidence only, not proof or authority."

