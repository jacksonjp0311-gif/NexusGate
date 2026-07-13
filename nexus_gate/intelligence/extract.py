from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .common import read_json, receipt_hash, sha_obj, write_json


CANDIDATE_DIR = Path("state") / "intelligence" / "candidates"
EXTRACT_REPORT = Path("reports") / "nexus_intelligence_extraction_latest.json"
LEDGER = Path("ledger") / "intelligence_candidates.jsonl"
VALID_POSITIVE = {"accepted", "accepted_with_modification"}
NEGATIVE = {"rejected", "reverted"}


def _candidate(interaction: dict[str, Any], kind: str, label: str, refs: list[str]) -> dict[str, Any]:
    negative = interaction.get("human_disposition") in NEGATIVE
    positive = interaction.get("human_disposition") in VALID_POSITIVE
    candidate = {
        "schema": "NEXUS_INTELLIGENCE_CANDIDATE.v2.9.0",
        "candidate_id": sha_obj({"interaction": interaction.get("interaction_id"), "kind": kind, "label": label})[:32],
        "candidate_type": kind,
        "normalized_label": label,
        "language_forms": sorted({label, label.replace("_", " ")}),
        "relations": [],
        "evidence_refs": refs,
        "interaction_ids": [interaction.get("interaction_id")],
        "experience_ids": [],
        "support": {
            "independent_occurrences": 1,
            "accepted_occurrences": 1 if positive else 0,
            "rejected_occurrences": 1 if negative else 0,
            "regression_occurrences": 0,
        },
        "quality": {
            "provenance_integrity": 1.0,
            "validation_strength": 1.0 if positive else 0.0,
            "causal_attribution": 0.5 if positive else 0.0,
            "stability": 0.0,
            "human_acceptance": 1.0 if positive else 0.0,
            "independent_repetition": 0.0,
            "combined_confidence": 0.5 if positive else 0.0,
        },
        "status": "candidate" if positive else "negative_evidence",
        "promotion_level": 1,
        "authority_boundary": {"may_change_routing": False, "may_execute": False, "may_authorize": False},
    }
    candidate["candidate_hash"] = receipt_hash(candidate)
    return candidate


def extract_from_interaction(root: str | Path, interaction_id: str) -> dict[str, Any]:
    root_path = Path(root)
    receipt = read_json(root_path / "state" / "ai_interactions" / interaction_id / "receipt.json", {})
    if not receipt:
        raise FileNotFoundError(interaction_id)
    change_set = receipt.get("change_set") or {}
    candidates: list[dict[str, Any]] = []
    for rel in change_set.get("changed_files") or []:
        candidates.append(_candidate(receipt, "repository_entity", rel, [f"ai_touch:{interaction_id}", f"file:{rel}"]))
    for rel, symbols in (change_set.get("touched_python_symbols") or {}).items():
        for symbol in symbols:
            candidates.append(_candidate(receipt, "procedural_skill", symbol, [f"ai_touch:{interaction_id}", f"symbol:{rel}:{symbol}"]))
    for name in change_set.get("touched_test_names") or []:
        candidates.append(_candidate(receipt, "test_expectation", name, [f"ai_touch:{interaction_id}", f"test:{name}"]))
    intent = ((receipt.get("human_intent") or {}).get("summary") or "").strip()
    if intent:
        candidates.append(_candidate(receipt, "intent_alias", intent.lower()[:120], [f"ai_touch:{interaction_id}:intent"]))
    for candidate in candidates:
        write_json(root_path / CANDIDATE_DIR / f"{candidate['candidate_id']}.json", candidate)
        append_hash_chained_event(root_path / LEDGER, {"event_type": "candidate_extracted", "candidate_id": candidate["candidate_id"], "candidate_hash": candidate["candidate_hash"], "interaction_id": interaction_id}, "intelligence-extract")
    report = {
        "schema": "NEXUS_INTELLIGENCE_EXTRACTION.v2.9.0",
        "status": "pass",
        "interaction_id": interaction_id,
        "candidate_count": len(candidates),
        "positive_candidates": len([c for c in candidates if c["status"] == "candidate"]),
        "negative_evidence": len([c for c in candidates if c["status"] == "negative_evidence"]),
        "claim_boundary": "Extraction creates candidates only. Promotion and conductance remain gated.",
    }
    write_json(root_path / EXTRACT_REPORT, report)
    return report


def status(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    candidates = sorted((root_path / CANDIDATE_DIR).glob("*.json"))
    return {"schema": "NEXUS_INTELLIGENCE_STATUS.v2.9.0", "status": "pass", "candidate_count": len(candidates), "ledger_chain": verify_hash_chain(root_path / LEDGER)}
