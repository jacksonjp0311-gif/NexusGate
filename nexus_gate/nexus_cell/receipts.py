from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict
def sha256_text(text: str)->str: return hashlib.sha256(text.encode("utf-8")).hexdigest()
def output_digest(stdout: str, stderr: str)->Dict[str,str]: return {"stdout_hash":sha256_text(stdout),"stderr_hash":sha256_text(stderr),"combined_hash":sha256_text(stdout+"\n"+stderr)}
def receipt_id(cell_id: str, invocation_id: str, stdout_hash: str, stderr_hash: str, ledger_hash: str)->str: return hashlib.sha256((cell_id+invocation_id+stdout_hash+stderr_hash+ledger_hash).encode("utf-8")).hexdigest()
def build_execution_receipt(*,cell_id: str,invocation_id: str,action: str,authority_decision: str,risk_score: float,capability_vector: Dict[str,int],runner: str,started_at: str,finished_at: str,exit_code: int,stdout: str,stderr: str,policy_hash: str,ledger_hash: str,claim_boundary: str)->Dict[str,Any]:
    d=output_digest(stdout,stderr); rid=receipt_id(cell_id,invocation_id,d["stdout_hash"],d["stderr_hash"],ledger_hash)
    return {"receipt_id":rid,"cell_id":cell_id,"invocation_id":invocation_id,"action":action,"authority_decision":authority_decision,"risk_score":risk_score,"capability_vector":capability_vector,"runner":runner,"started_at":started_at,"finished_at":finished_at,"exit_code":exit_code,"stdout_hash":d["stdout_hash"],"stderr_hash":d["stderr_hash"],"output_digest":d,"policy_hash":policy_hash,"ledger_hash":ledger_hash,"claim_boundary":claim_boundary}
def write_receipt(path: Path, receipt: Dict[str,Any])->None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
