from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import sha_obj, utc, write_json
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .state import ensure_dirs, latest_epoch


def begin_cognitive_cycle(root: str | Path, prompt: str = "") -> dict[str, Any]:
    paths = ensure_dirs(root)
    epoch = latest_epoch(root)
    cycle_id = "cycle_" + sha_obj({"prompt": prompt, "epoch": epoch, "created_at_utc": utc()})[:24]
    cycle = {
        "schema": "NEXUS_COGNITIVE_CYCLE.v2.10.0",
        "cycle_id": cycle_id,
        "stage": "build",
        "started_at_utc": utc(),
        "source_epoch_id": epoch["source_epoch_id"],
        "teach": {"episode_created": False},
        "build": {},
        "learn": {"proposal_created": False},
        "verify": {},
        "inner_communication": {"message_count": 0},
        "model_before": {},
        "model_after": {},
        "authority_invariants": {"may_execute": False, "may_authorize": False, "may_mutate_source": False},
        "measured_improvement": {"status": "not_evaluated"},
        "status": "open",
        "claim_boundary": "Cognitive cycles coordinate evidence. They do not authorize action or apply learning.",
    }
    write_json(paths["cycles"] / f"{cycle_id}.json", cycle)
    append_hash_chained_event(Path(root) / "ledger" / "nex_cognitive_cycles.jsonl", {"schema": "NEXUS_COGNITIVE_CYCLE_EVENT.v2.10.0", "event_type": "cycle_begin", "cycle_id": cycle_id, "source_epoch_id": epoch["source_epoch_id"]}, producer="nex-cycle")
    return cycle


def finalize_cognitive_cycle(root: str | Path, cycle: dict[str, Any], status: str = "pass") -> dict[str, Any]:
    paths = ensure_dirs(root)
    cycle = dict(cycle)
    cycle["stage"] = "verified"
    cycle["completed_at_utc"] = utc()
    cycle["status"] = status
    write_json(paths["cycles"] / f"{cycle['cycle_id']}.json", cycle)
    write_json(paths["reports"] / "nexus_cognitive_cycle_latest.json", cycle)
    append_hash_chained_event(Path(root) / "ledger" / "nex_cognitive_cycles.jsonl", {"schema": "NEXUS_COGNITIVE_CYCLE_EVENT.v2.10.0", "event_type": "cycle_finalize", "cycle_id": cycle["cycle_id"], "status": status}, producer="nex-cycle")
    return cycle


def cycle_status(root: str | Path) -> dict[str, Any]:
    paths = ensure_dirs(root)
    cycles = sorted(paths["cycles"].glob("cycle_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    chain = verify_hash_chain(Path(root) / "ledger" / "nex_cognitive_cycles.jsonl")
    latest = None
    if cycles:
        import json

        latest = json.loads(cycles[0].read_text(encoding="utf-8-sig"))
    return {"schema": "NEXUS_CYCLE_STATUS.v2.10.0", "status": "pass" if chain["chain_valid"] else "fail", "cycle_count": len(cycles), "latest_cycle_id": latest.get("cycle_id") if latest else None, "chain": chain}
