from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

VERSION = "0.8.8"
CONTROLLED_LANES: Dict[str, Dict[str, object]] = {
    "status":{"argv":["python","-m","nexus_gate.nexus_shell.shell","--root",".","--command","status","--intent","NexusCell controlled status lane","--json"],"mutates":False,"description":"Build NexusShell status packet."},
    "compile":{"argv":["python","-m","nexus_gate.compiler","--root",".","--json"],"mutates":False,"description":"Run gated compiler."},
    "tests":{"argv":["python","-m","unittest","discover","-s","tests"],"mutates":False,"description":"Run tests."},
    "cell-plan":{"argv":["python","-m","nexus_gate.nexus_cell.plan","--root",".","--intent","NexusCell controlled planner lane","--json"],"mutates":False,"description":"Build planner packet."},
    "cell-context":{"argv":["python","-m","nexus_gate.nexus_cell.context_bridge","--root",".","--intent","NexusCell controlled context lane","--json"],"mutates":False,"description":"Build context packet."},
    "cell-bridge":{"argv":["python","-m","nexus_gate.nexus_cell.bridge","--root",".","--intent","NexusCell controlled bridge lane","--json"],"mutates":False,"description":"Build core bridge packet."},
}
FORBIDDEN_CAPABILITIES=["network","secrets","service_install","registry","host_mount","git_write"]
BOUNDARY={"arbitrary_command_execution":False,"network_enabled":False,"secrets_enabled":False,"host_mount_enabled":False,"git_write_enabled":False,"rollback_claim_enabled":False,"self_authorization_enabled":False}
DEFAULT_POLICY={"version":"0.1.0","default":"deny","thresholds":{"auto":0.30,"review":0.65},"rules":[{"name":"allow_mock_local_readonly","match":{"runner":"mock"},"action":{"allow":True,"audit":"metadata"}}],"hard_denies":["raw_secret_exposure","service_install_without_authority","registry_write_without_authority","unrestricted_network","git_push_without_authority"]}

def list_lanes(): return sorted(CONTROLLED_LANES)
def lane_policy(lane: str) -> Dict[str,object]:
    if lane not in CONTROLLED_LANES: return {"lane":lane,"known":False,"allowed":False,"reason":"unknown_lane","boundary":BOUNDARY}
    p=dict(CONTROLLED_LANES[lane]); p.update({"lane":lane,"known":True,"allowed":True,"reason":"controlled_internal_lane","boundary":BOUNDARY}); return p
def capability_policy(capability_vector: Dict[str,object]) -> Dict[str,object]:
    active=sorted([k for k,v in capability_vector.items() if bool(v)])
    forbidden=sorted([k for k in active if k in FORBIDDEN_CAPABILITIES])
    return {"active_capabilities":active,"forbidden_active":forbidden,"allowed":len(forbidden)==0,"required_response":"deny_or_shadow" if forbidden else "read_only_lane_ok"}
def policy_path(root: Path) -> Path: return root/"state"/"nexus_cell"/"gate_policy.v0.1.json"
def ensure_policy(root: Path) -> Dict[str,Any]:
    p=policy_path(root); p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists(): p.write_text(json.dumps(DEFAULT_POLICY,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return load_policy(root)
def load_policy(root: Path) -> Dict[str,Any]:
    p=policy_path(root)
    if not p.exists(): return DEFAULT_POLICY.copy()
    return json.loads(p.read_text(encoding="utf-8-sig"))
def first_match(request: Mapping[str,Any], rules: Iterable[Mapping[str,Any]]):
    for rule in rules:
        match=rule.get("match",{})
        if all(request.get(k)==v for k,v in match.items()): return dict(rule)
    return None
def evaluate_policy(request: Mapping[str,Any], policy: Mapping[str,Any]) -> Dict[str,Any]:
    rule=first_match(request, policy.get("rules",[]))
    if rule is None: return {"allow":False,"rule":None,"audit":"security_event","reason":"default_deny"}
    action=dict(rule.get("action",{}))
    return {"allow":bool(action.get("allow",False)),"rule":rule.get("name"),"audit":action.get("audit","metadata"),"reason":"first_match"}
def policy_hash(policy: Mapping[str,Any]) -> str:
    return hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
