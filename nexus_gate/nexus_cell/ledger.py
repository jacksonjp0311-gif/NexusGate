from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict

GENESIS_HASH=hashlib.sha256(b"NEXUS_CELL_GENESIS").hexdigest()
def canonical_json(payload: Dict[str,Any]) -> str: return json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def event_hash(event_without_hashes: Dict[str,Any]) -> str: return hashlib.sha256(canonical_json(event_without_hashes).encode("utf-8")).hexdigest()
def ledger_hash(event_hash_value: str, previous_ledger_hash: str|None=None) -> str: return hashlib.sha256((event_hash_value+(previous_ledger_hash or GENESIS_HASH)).encode("utf-8")).hexdigest()
def ledger_path(root: Path)->Path: return root/"ledger"/"nexus_cell"/"continuity.jsonl"
def top_level_ledger_path(root: Path)->Path: return root/"NexusCell"/"ledger"/"nexus_cell_continuity.jsonl"
def read_events(root: Path):
    p=ledger_path(root)
    if not p.exists(): return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
def latest_ledger_hash(root: Path)->str:
    ev=read_events(root); return ev[-1]["ledger_hash"] if ev else GENESIS_HASH
def append_event(root: Path, event: Dict[str,Any]) -> Dict[str,Any]:
    clean={k:v for k,v in event.items() if k not in {"event_hash","ledger_hash","previous_ledger_hash"}}
    prev=latest_ledger_hash(root); eh=event_hash(clean); lh=ledger_hash(eh,prev)
    stored=dict(clean); stored.update({"event_hash":eh,"previous_ledger_hash":prev,"ledger_hash":lh})
    for p in [ledger_path(root), top_level_ledger_path(root)]:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a",encoding="utf-8") as h: h.write(canonical_json(stored)+"\n")
    return stored
def ledger_summary(root: Path)->Dict[str,Any]:
    ev=read_events(root); return {"count":len(ev),"latest_ledger_hash":latest_ledger_hash(root),"latest_event":ev[-1] if ev else None}
