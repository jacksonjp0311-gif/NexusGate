from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FailureSeverity = Literal["info", "warning", "block", "critical"]


@dataclass(frozen=True)
class FailureMode:
    failure_id: str
    name: str
    severity: FailureSeverity
    trigger: str
    required_response: str
    claim_boundary: str = "Failure mode classification is a local development signal, not a safety proof."
