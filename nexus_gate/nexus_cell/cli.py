from __future__ import annotations
import argparse, datetime as _dt, json, uuid
from pathlib import Path
from typing import Any
from nexus_gate.nexus_cell import CLAIM_BOUNDARY, NEXUS_CELL_VERSION
from nexus_gate.nexus_cell.authority import decide_authority
from nexus_gate.nexus_cell.ledger import append_event, ledger_summary
from nexus_gate.nexus_cell.policy import ensure_policy, evaluate_policy, policy_hash
from nexus_gate.nexus_cell.receipts import build_execution_receipt, write_receipt
from nexus_gate.nexus_cell.risk import capability_vector_from_action, score_risk
from nexus_gate.nexus_cell.runners.mock_runner import MockRunner
from nexus_gate.nexus_cell.seals import build_return_seal
from nexus_gate.nexus_cell.secrets.redaction import contains_raw_secret, redact_text
CELL_ID="nexus_cell_local_dev_v0_1"
def _utc_now(): return _dt.datetime.now(_dt.timezone.utc).isoformat()
def _json_print(payload: dict[str,Any])->int: print(json.dumps(payload,indent=2,sort_keys=True)); return 0
def ensure_layout(root: Path)->None:
    for rel in ["NexusCell/state","NexusCell/ledger","NexusCell/runtime/wsb","state/nexus_cell","ledger/nexus_cell","reports/nexus_cell"]: (root/rel).mkdir(parents=True,exist_ok=True)
    ensure_policy(root)
def doctor(root: Path)->dict[str,Any]:
    ensure_layout(root)
    required=["NexusCell/README.md","NexusCell/NEXUS_CELL_ARCHITECTURE.md","NexusCell/NEXUS_CELL_PORT_MAP.md","NexusCell/NEXUS_CELL_SECURITY_MODEL.md","NexusCell/NEXUS_CELL_MATH_AND_ALGORITHMS.md","NexusCell/examples/hello.ps1","state/nexus_cell/nexus_cell_manifest.v0.1.json","state/nexus_cell/gate_policy.v0.1.json","ledger/nexus_cell/continuity.jsonl"]
    missing=[rel for rel in required if not (root/rel).exists()]
    return {"ok":len(missing)==0,"version":NEXUS_CELL_VERSION,"mode":"doctor","missing":missing,"ledger":ledger_summary(root),"claim_boundary":CLAIM_BOUNDARY}
def policy_cmd(root: Path)->dict[str,Any]:
    ensure_layout(root); p=ensure_policy(root); return {"ok":True,"version":NEXUS_CELL_VERSION,"policy":p,"policy_hash":policy_hash(p),"claim_boundary":CLAIM_BOUNDARY}
def ledger_cmd(root: Path)->dict[str,Any]:
    ensure_layout(root); return {"ok":True,"version":NEXUS_CELL_VERSION,"ledger":ledger_summary(root),"claim_boundary":CLAIM_BOUNDARY}
def run_cmd(root: Path, runner: str, payload: str, authority_scope: list[str]|None=None)->dict[str,Any]:
    ensure_layout(root); started_at=_utc_now()
    payload_path=(root/payload).resolve() if not Path(payload).is_absolute() else Path(payload)
    action=f"run payload with runner {runner}: {payload_path.name}"; pol=ensure_policy(root); p_hash=policy_hash(pol)
    caps=capability_vector_from_action(action=action,runner=runner,payload=str(payload_path)); risk_score=score_risk(caps)
    raw=payload_path.read_text(encoding="utf-8-sig") if payload_path.exists() else ""; hard_deny=contains_raw_secret(raw)
    policy_decision=evaluate_policy({"runner":runner},pol)
    authority=decide_authority(action,policy_decision,caps,authority_scope or ["local_development_operator"],True,hard_deny,pol.get("thresholds"))
    if runner!="mock":
        result={"exit_code":64,"stdout":"","stderr":f"runner {runner} is scaffolded but not enabled in v0.1","backend":runner,"claim_boundary":"Only mock runner is active in portable tests."}
    elif authority["decision"] in {"deny","reject","escalate"}:
        result={"exit_code":73,"stdout":"","stderr":f"authority denied: {authority['reason']}","backend":runner,"claim_boundary":"Denied invocations do not execute."}
    else:
        rr=MockRunner().run(payload_path); result={"exit_code":rr.exit_code,"stdout":redact_text(rr.stdout),"stderr":redact_text(rr.stderr),"backend":rr.backend,"claim_boundary":rr.claim_boundary}
    finished_at=_utc_now(); invocation_id=str(uuid.uuid4())
    event=append_event(root,{"type":"execution_invocation","version":NEXUS_CELL_VERSION,"cell_id":CELL_ID,"invocation_id":invocation_id,"runner":runner,"payload":str(payload_path),"authority_decision":authority["decision"],"risk_score":risk_score,"capability_vector":caps,"exit_code":result["exit_code"],"started_at":started_at,"finished_at":finished_at,"claim_boundary":CLAIM_BOUNDARY})
    receipt=build_execution_receipt(cell_id=CELL_ID,invocation_id=invocation_id,action=action,authority_decision=authority["decision"],risk_score=risk_score,capability_vector=caps,runner=runner,started_at=started_at,finished_at=finished_at,exit_code=int(result["exit_code"]),stdout=str(result["stdout"]),stderr=str(result["stderr"]),policy_hash=p_hash,ledger_hash=event["ledger_hash"],claim_boundary=CLAIM_BOUNDARY)
    receipt_path=root/"reports"/"nexus_cell"/"receipt_latest.json"; write_receipt(receipt_path,receipt)
    seal=build_return_seal(cell_id=CELL_ID,origin_image_id="mock_origin_image",backend="hash_only",state_digest=receipt["output_digest"]["combined_hash"],created_at=finished_at,policy_hash=p_hash)
    return {"ok":result["exit_code"]==0,"version":NEXUS_CELL_VERSION,"mode":"run","runner":runner,"authority":authority,"risk_score":risk_score,"capability_vector":caps,"execution":result,"receipt":receipt,"receipt_path":str(receipt_path),"ledger_event":event,"return_seal":seal,"claim_boundary":CLAIM_BOUNDARY}
def main(argv: list[str]|None=None)->int:
    parser=argparse.ArgumentParser(prog="nexus-cell",description="NexusCell execution-governance CLI"); sub=parser.add_subparsers(dest="cmd",required=True)
    d=sub.add_parser("doctor"); d.add_argument("--root",default=".")
    r=sub.add_parser("run"); r.add_argument("--root",default="."); r.add_argument("--runner",default="mock",choices=["mock","windows_sandbox","hyperv_container","hyperv_vm"]); r.add_argument("--payload",required=True)
    l=sub.add_parser("ledger"); l.add_argument("--root",default=".")
    p=sub.add_parser("policy"); p.add_argument("--root",default=".")
    args=parser.parse_args(argv); root=Path(getattr(args,"root",".")).resolve()
    if args.cmd=="doctor": return _json_print(doctor(root))
    if args.cmd=="run":
        payload=run_cmd(root,args.runner,args.payload); _json_print(payload); return 0 if payload["ok"] else 1
    if args.cmd=="ledger": return _json_print(ledger_cmd(root))
    if args.cmd=="policy": return _json_print(policy_cmd(root))
    return 2
if __name__=="__main__": raise SystemExit(main())
