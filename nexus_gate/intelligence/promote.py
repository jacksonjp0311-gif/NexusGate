from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .common import read_json, receipt_hash, write_json


PROMOTED = Path("state") / "intelligence" / "promoted"
PROMOTION_LEDGER = Path("ledger") / "intelligence_promotions.jsonl"
REPORT = Path("reports") / "nexus_intelligence_promotion_latest.json"


def list_candidates(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    items = [read_json(path, {}) for path in sorted((root_path / "state" / "intelligence" / "candidates").glob("*.json"))]
    return {"schema": "NEXUS_INTELLIGENCE_CANDIDATES.v2.9.0", "status": "pass", "candidates": [item for item in items if item]}


def promote(root: str | Path, candidate_id: str, level: int = 2, human_authorized: bool = False) -> dict[str, Any]:
    root_path = Path(root)
    candidate = read_json(root_path / "state" / "intelligence" / "candidates" / f"{candidate_id}.json", {})
    blockers: list[str] = []
    if not candidate:
        blockers.append("candidate_missing")
    if candidate and candidate.get("candidate_hash") != receipt_hash(candidate):
        blockers.append("candidate_hash_invalid")
    if candidate and candidate.get("status") != "candidate":
        blockers.append("not_positive_candidate")
    if level >= 5 and not human_authorized:
        blockers.append("level_5_requires_explicit_human_authorization")
    if level >= 5 and (candidate.get("support") or {}).get("independent_occurrences", 0) < 3:
        blockers.append("level_5_requires_repeated_verified_support")
    if blockers:
        report = {"schema": "NEXUS_INTELLIGENCE_PROMOTION.v2.9.0", "status": "blocked", "candidate_id": candidate_id, "blockers": blockers}
        write_json(root_path / REPORT, report)
        return report
    promoted = dict(candidate)
    promoted["promotion_level"] = max(int(promoted.get("promotion_level") or 1), level)
    promoted["status"] = "promoted"
    promoted["candidate_hash"] = receipt_hash(promoted)
    write_json(root_path / PROMOTED / f"{candidate_id}.json", promoted)
    append_hash_chained_event(root_path / PROMOTION_LEDGER, {"event_type": "intelligence_promoted", "candidate_id": candidate_id, "promotion_level": level, "candidate_hash": promoted["candidate_hash"]}, "intelligence-promote")
    report = {"schema": "NEXUS_INTELLIGENCE_PROMOTION.v2.9.0", "status": "pass", "candidate_id": candidate_id, "promotion_level": level}
    write_json(root_path / REPORT, report)
    return report


def reject(root: str | Path, candidate_id: str) -> dict[str, Any]:
    root_path = Path(root)
    append_hash_chained_event(root_path / PROMOTION_LEDGER, {"event_type": "intelligence_rejected", "candidate_id": candidate_id}, "intelligence-reject")
    return {"schema": "NEXUS_INTELLIGENCE_PROMOTION.v2.9.0", "status": "rejected", "candidate_id": candidate_id}


def replay_verify(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    candidate_chain = verify_hash_chain(root_path / "ledger" / "intelligence_candidates.jsonl")
    promotion_chain = verify_hash_chain(root_path / PROMOTION_LEDGER)
    return {
        "schema": "NEXUS_INTELLIGENCE_REPLAY.v2.9.0",
        "status": "pass" if candidate_chain["chain_valid"] and promotion_chain["chain_valid"] else "fail",
        "candidate_chain": candidate_chain,
        "promotion_chain": promotion_chain,
    }
