from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import read_json, sha_obj, sha_text, utc, write_json
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .state import ensure_dirs, latest_epoch


TEACH_LEDGER = Path("ledger") / "nex_teaching_events.jsonl"
VALID_DISPOSITIONS = {"pending_review", "accepted", "accepted_with_modification", "rejected", "abandoned", "reverted"}
STAGE_FILES = {
    "begin": "00_begin.json",
    "evidence": "10_evidence.json",
    "validation": "20_validation.json",
    "disposition": "30_disposition.json",
    "seal": "40_teaching_seal.json",
}


def _teaching_dir(root: str | Path, teaching_id: str) -> Path:
    return ensure_dirs(root)["teaching"] / teaching_id


def _append_stage(root: str | Path, teaching_id: str, event_type: str, sequence: int, payload: dict[str, Any]) -> dict[str, Any]:
    epoch = latest_epoch(root)
    event = {
        "schema": "NEXUS_TEACHING_EVENT.v2.10.0",
        "event_type": event_type,
        "teaching_id": teaching_id,
        "sequence": sequence,
        "payload_hash": sha_obj(payload),
        "source_epoch_id": epoch["source_epoch_id"],
        "source_root": epoch["source_root"],
    }
    return append_hash_chained_event(Path(root) / TEACH_LEDGER, event, producer="nex-teach")


def _write_stage(root: str | Path, teaching_id: str, stage: str, payload: dict[str, Any], sequence: int) -> dict[str, Any]:
    directory = _teaching_dir(root, teaching_id)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / STAGE_FILES[stage]
    if path.exists():
        existing = read_json(path, {})
        if sha_obj(existing) != sha_obj(payload):
            return {"status": "fail", "reason": "immutable_stage_mismatch", "path": str(path)}
        return {"status": "verified_existing", "path": str(path), "payload_hash": sha_obj(existing)}
    write_json(path, payload)
    appended = _append_stage(root, teaching_id, stage, sequence, payload)
    return {"status": "pass", "path": str(path), "event_hash": appended["event_hash"], "payload_hash": sha_obj(payload)}


def begin_teaching_episode(root: str | Path, tag: str, teacher_type: str = "human_instruction") -> dict[str, Any]:
    epoch = latest_epoch(root)
    teaching_id = "teach_" + sha_obj({"tag": tag, "epoch": epoch, "created_at_utc": utc()})[:24]
    payload = {
        "schema": "NEXUS_TEACHING_STAGE_BEGIN.v2.10.0",
        "teaching_id": teaching_id,
        "status": "open",
        "teacher_type": teacher_type,
        "intent": {"summary": tag or "NEX teaching episode", "intent_hash": sha_text(tag or "")},
        "source_epoch_id": epoch["source_epoch_id"],
        "source_root": epoch["source_root"],
        "created_at_utc": utc(),
        "authority_boundary": {"may_create_candidates": True, "may_apply_learning": False, "may_execute": False, "may_authorize": False},
    }
    result = _write_stage(root, teaching_id, "begin", payload, 0)
    return {"schema": "NEXUS_TEACH_BEGIN_RESULT.v2.10.0", "status": result["status"], "teaching_id": teaching_id, "stage": result}


def bind_teaching_evidence(root: str | Path, teaching_id: str, refs: list[str] | None = None) -> dict[str, Any]:
    payload = {
        "schema": "NEXUS_TEACHING_STAGE_EVIDENCE.v2.10.0",
        "teaching_id": teaching_id,
        "created_at_utc": utc(),
        "evidence_refs": refs or [],
        "ai_interaction_refs": [],
        "experience_refs": [],
    }
    result = _write_stage(root, teaching_id, "evidence", payload, 10)
    return {"schema": "NEXUS_TEACH_EVIDENCE_RESULT.v2.10.0", "status": result["status"], "teaching_id": teaching_id, "stage": result}


def bind_teaching_validation(root: str | Path, teaching_id: str, validation_bundle_id: str = "") -> dict[str, Any]:
    tests = [validation_bundle_id] if validation_bundle_id else []
    payload = {
        "schema": "NEXUS_TEACHING_STAGE_VALIDATION.v2.10.0",
        "teaching_id": teaching_id,
        "created_at_utc": utc(),
        "validation": {
            "tests_executed": tests,
            "test_exit_codes": [],
            "test_report_hashes": [sha_text(validation_bundle_id)] if validation_bundle_id else [],
            "evolve_report_hash": None,
            "action_validation_refs": [],
            "experience_seal_refs": [],
        },
    }
    result = _write_stage(root, teaching_id, "validation", payload, 20)
    return {"schema": "NEXUS_TEACH_VALIDATION_RESULT.v2.10.0", "status": result["status"], "teaching_id": teaching_id, "stage": result}


def compute_teaching_quality(episode: dict[str, Any]) -> dict[str, float]:
    disposition = episode.get("human_disposition") or "pending_review"
    validation = episode.get("validation") or {}
    accepted = disposition in {"accepted", "accepted_with_modification"}
    tests = validation.get("tests_executed") or []
    experience_refs = episode.get("experience_refs") or validation.get("experience_seal_refs") or []
    independent = float(episode.get("support", {}).get("independent_verified", 1 if tests else 0))
    p = 1.0 if episode.get("source_epoch_id") else 0.0
    v = 1.0 if tests else 0.0
    a = 1.0 if experience_refs else (0.35 if tests else 0.0)
    s = float(episode.get("later_stability", 0.0))
    h = 1.0 if accepted else 0.0
    r = min(1.0, independent / 3.0)
    values = [p, v, a, s, h, r]
    product = 1.0
    for value in values:
        product *= max(0.0, min(1.0, value))
    return {
        "provenance_integrity": round(p, 6),
        "validation_strength": round(v, 6),
        "causal_attribution": round(a, 6),
        "later_stability": round(s, 6),
        "human_acceptance": round(h, 6),
        "independent_repetition": round(r, 6),
        "gate_quality": round(min(values), 6),
        "ranking_quality": round(product ** (1.0 / 6.0), 6),
    }


def seal_teaching_episode(root: str | Path, teaching_id: str, disposition: str = "pending_review") -> dict[str, Any]:
    if disposition not in VALID_DISPOSITIONS:
        return {"schema": "NEXUS_TEACH_SEAL_RESULT.v2.10.0", "status": "fail", "reason": "invalid_disposition", "teaching_id": teaching_id}
    directory = _teaching_dir(root, teaching_id)
    begin = read_json(directory / STAGE_FILES["begin"], {})
    if not begin:
        return {"schema": "NEXUS_TEACH_SEAL_RESULT.v2.10.0", "status": "fail", "reason": "missing_begin_stage", "teaching_id": teaching_id}
    evidence = read_json(directory / STAGE_FILES["evidence"], {})
    validation_stage = read_json(directory / STAGE_FILES["validation"], {})
    validation = validation_stage.get("validation") or {"tests_executed": [], "test_exit_codes": [], "test_report_hashes": [], "evolve_report_hash": None, "action_validation_refs": [], "experience_seal_refs": []}
    disposition_payload = {
        "schema": "NEXUS_TEACHING_STAGE_DISPOSITION.v2.10.0",
        "teaching_id": teaching_id,
        "created_at_utc": utc(),
        "human_disposition": disposition,
    }
    disposition_result = _write_stage(root, teaching_id, "disposition", disposition_payload, 30)
    if disposition_result.get("status") == "fail":
        return {"schema": "NEXUS_TEACH_SEAL_RESULT.v2.10.0", "status": "fail", "reason": disposition_result.get("reason"), "teaching_id": teaching_id, "stage": disposition_result}
    episode = {
        "schema": "NEXUS_TEACHING_EPISODE.v2.10.0",
        "teaching_id": teaching_id,
        "status": "sealed",
        "teacher_type": begin.get("teacher_type", "human_instruction"),
        "intent": begin.get("intent", {}),
        "evidence_refs": evidence.get("evidence_refs", []),
        "ai_interaction_refs": evidence.get("ai_interaction_refs", []),
        "experience_refs": evidence.get("experience_refs", []),
        "source_epoch_id": begin.get("source_epoch_id"),
        "validation": validation,
        "human_disposition": disposition,
        "contradictions": [],
        "regressions": [],
        "negative_evidence": disposition in {"rejected", "abandoned", "reverted"},
        "authority_boundary": {"may_create_candidates": True, "may_apply_learning": False, "may_execute": False, "may_authorize": False},
    }
    episode["quality"] = compute_teaching_quality(episode)
    episode["teaching_seal_hash"] = sha_obj({k: v for k, v in episode.items() if k != "teaching_seal_hash"})
    result = _write_stage(root, teaching_id, "seal", episode, 40)
    return {"schema": "NEXUS_TEACH_SEAL_RESULT.v2.10.0", "status": result["status"], "teaching_id": teaching_id, "disposition_stage": disposition_result, "seal": episode}


def verify_teaching_episode(root: str | Path, teaching_id: str) -> dict[str, Any]:
    directory = _teaching_dir(root, teaching_id)
    errors: list[str] = []
    previous = -1
    for sequence, stage in [(0, "begin"), (10, "evidence"), (20, "validation"), (30, "disposition"), (40, "seal")]:
        path = directory / STAGE_FILES[stage]
        if not path.exists():
            if stage in {"evidence", "validation"}:
                continue
            errors.append(f"missing_stage:{stage}")
            continue
        if sequence <= previous:
            errors.append(f"invalid_stage_order:{stage}")
        previous = sequence
    seal = read_json(directory / STAGE_FILES["seal"], {})
    if seal:
        expected = sha_obj({k: v for k, v in seal.items() if k != "teaching_seal_hash"})
        if seal.get("teaching_seal_hash") != expected:
            errors.append("teaching_seal_hash_mismatch")
        if not seal.get("source_epoch_id"):
            errors.append("missing_source_epoch_binding")
    chain = verify_hash_chain(Path(root) / TEACH_LEDGER)
    if not chain["chain_valid"]:
        errors.append("teaching_ledger_invalid")
    return {"schema": "NEXUS_TEACH_VERIFY.v2.10.0", "status": "pass" if not errors else "fail", "teaching_id": teaching_id, "errors": errors, "chain": chain}


def status(root: str | Path) -> dict[str, Any]:
    teaching = ensure_dirs(root)["teaching"]
    episodes = sorted(path.name for path in teaching.glob("teach_*") if path.is_dir())
    chain = verify_hash_chain(Path(root) / TEACH_LEDGER)
    return {"schema": "NEXUS_TEACH_STATUS.v2.10.0", "status": "pass" if chain["chain_valid"] else "fail", "teaching_count": len(episodes), "teaching_ids": episodes[-20:], "chain": chain}


def replay_verify(root: str | Path) -> dict[str, Any]:
    base = Path(root)
    chain = verify_hash_chain(base / TEACH_LEDGER)
    errors: list[str] = []
    seen_payloads: set[str] = set()
    if (base / TEACH_LEDGER).exists():
        for line in (base / TEACH_LEDGER).read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("payload_hash") in seen_payloads and event.get("event_type") != "status":
                errors.append(f"duplicate_payload:{event.get('teaching_id')}")
            seen_payloads.add(str(event.get("payload_hash")))
    return {"schema": "NEXUS_TEACH_REPLAY.v2.10.0", "status": "pass" if chain["chain_valid"] and not errors else "fail", "chain": chain, "errors": errors, "claim_boundary": "Teaching replay verifies episodes; it does not apply learning."}
