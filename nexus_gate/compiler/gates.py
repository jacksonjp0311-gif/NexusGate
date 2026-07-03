from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

GateStatus = Literal["pass", "fail", "warn"]


@dataclass(frozen=True)
class GateResult:
    gate: str
    status: GateStatus
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def failed(self) -> bool:
        return self.status == "fail"
