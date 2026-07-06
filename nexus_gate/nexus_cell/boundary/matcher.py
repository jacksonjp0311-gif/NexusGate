from __future__ import annotations
from typing import Any, Mapping
def host_matches(pattern: str, host: str)->bool:
    pattern=pattern.lower(); host=host.lower()
    if pattern.startswith("*."):
        suffix=pattern[2:]
        return host.endswith("."+suffix) and host != suffix
    return pattern == host
def field_matches(key: str, expected: Any, actual: Any)->bool:
    if key=="host" and isinstance(expected,str) and isinstance(actual,str): return host_matches(expected,actual)
    return expected == actual
def match_rule(rule: Mapping[str,Any], request: Mapping[str,Any])->bool:
    return all(k in request and field_matches(k,v,request.get(k)) for k,v in rule.get("match",{}).items())
