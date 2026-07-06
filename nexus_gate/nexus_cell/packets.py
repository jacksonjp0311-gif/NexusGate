from dataclasses import dataclass, field
from typing import Any
@dataclass(frozen=True)
class NexusCellInvocationPacket:
    cell_id: str
    invocation_id: str
    action: str
    runner: str
    payload: str
    capability_vector: dict[str,int]
    authority_scope: list[str] = field(default_factory=list)
    metadata: dict[str,Any] = field(default_factory=dict)
