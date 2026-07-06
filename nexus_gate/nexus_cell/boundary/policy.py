from __future__ import annotations
from typing import Any, Iterable, Mapping
from nexus_gate.nexus_cell.boundary.matcher import match_rule
def boundary_decision(request: Mapping[str,Any], rules: Iterable[Mapping[str,Any]]) -> dict[str,Any]:
    for rule in rules:
        if match_rule(rule,request): return {"action":rule.get("action","deny"),"rule":rule.get("name"),"audit":"metadata" if rule.get("action")=="allow" else "security_event"}
    return {"action":"deny","rule":None,"audit":"security_event"}
