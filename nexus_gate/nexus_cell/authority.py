from __future__ import annotations
from typing import Any, Dict, List, Mapping
from nexus_gate.nexus_cell.risk import risk_band, score_risk

VERSION = "0.8.8"

def evaluate_authority(lane_policy: Dict[str,object], capability_policy: Dict[str,object], human_authorized: bool=False, execute_requested: bool=False) -> Dict[str,object]:
    reasons: List[str]=[]
    if not lane_policy.get("known"): reasons.append("unknown_lane")
    if not lane_policy.get("allowed"): reasons.append("lane_not_allowed")
    if not capability_policy.get("allowed"): reasons.append("forbidden_capability_active")
    if execute_requested and not human_authorized: reasons.append("execution_requires_human_authorization")
    may_build = lane_policy.get("known") is True and lane_policy.get("allowed") is True
    may_execute = may_build and capability_policy.get("allowed") is True and human_authorized is True and execute_requested is True
    return {"version":VERSION,"may_build_packet":bool(may_build),"may_execute_controlled_lane":bool(may_execute),"human_authorized":bool(human_authorized),"execute_requested":bool(execute_requested),"decision":"allow_controlled_execution" if may_execute else ("packet_only" if may_build else "deny"),"reasons":reasons,"boundary":"Authority applies only to controlled internal lanes. It is not arbitrary shell authority."}

def decide_authority(action: str, policy_decision: Mapping[str,Any], capability_vector: Mapping[str,int], authority_scope: list[str]|None=None, schema_present: bool=True, hard_deny: bool=False, thresholds: Mapping[str,float]|None=None) -> Dict[str,Any]:
    authority_scope=authority_scope or []
    risk_score=score_risk(capability_vector); band=risk_band(risk_score, thresholds)
    if not schema_present: decision,reason="reject","schema_missing"
    elif hard_deny: decision,reason="deny","hard_deny_policy_match"
    elif not policy_decision.get("allow"): decision,reason="deny",policy_decision.get("reason","policy_default_deny")
    elif not authority_scope and any(capability_vector.get(k,0) for k in ["fs_write","git_write","registry","service_install","network","secrets","host_mount"]): decision,reason="shadow","authority_missing"
    elif band=="deny": decision,reason="escalate","risk_exceeds_review_threshold"
    elif band=="review": decision,reason="shadow","risk_exceeds_auto_threshold"
    else: decision,reason="engage","authority_present_and_risk_allowed"
    return {"action":action,"decision":decision,"reason":reason,"risk_score":risk_score,"risk_band":band,"authority_scope":authority_scope}
