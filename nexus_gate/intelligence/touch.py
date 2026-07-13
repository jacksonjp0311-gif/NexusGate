from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .common import changed_files, git_commit, git_status_hash, latest_epoch, patch_hash, read_json, receipt_hash, run_git, sha_obj, sha_text, utc, write_json
from .redact import quarantine_report, redact_text


STATE = Path("state") / "ai_interactions"
LEDGER = Path("ledger") / "ai_interactions.jsonl"
REPORT = Path("reports") / "nexus_ai_touch_latest.json"
VERIFY_REPORT = Path("reports") / "nexus_ai_touch_verify_latest.json"
VALID_DISPOSITIONS = {"pending_review", "accepted", "accepted_with_modification", "rejected", "abandoned", "reverted"}


def _pre_state(root: Path) -> dict[str, Any]:
    epoch = latest_epoch(root)
    return {
        "source_epoch_id": epoch.get("source_epoch_id"),
        "source_root": epoch.get("source_root"),
        "git_commit": git_commit(root),
        "git_status_hash": git_status_hash(root),
        "repository_snapshot_hash": sha_obj({"commit": git_commit(root), "status": git_status_hash(root)}),
    }


def _symbols(root: Path, files: list[str]) -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}
    for rel in files:
        if not rel.endswith(".py"):
            continue
        path = root / rel
        if not path.exists():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        names = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
        if names:
            output[rel] = sorted(set(names))
    return output


def _test_names(root: Path, files: list[str]) -> list[str]:
    names: set[str] = set()
    for rel in files:
        if not rel.startswith("tests/") or not rel.endswith(".py"):
            continue
        path = root / rel
        if not path.exists():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.add(node.name)
    return sorted(names)


def begin(root: str | Path, provider: str, session_id: str, intent: str, model_identifier: str | None = None) -> dict[str, Any]:
    root_path = Path(root)
    redacted_intent, redaction = redact_text(intent)
    interaction_id = sha_obj({"provider": provider, "session": sha_text(session_id), "intent": sha_text(redacted_intent), "started": utc()})[:32]
    receipt = {
        "schema": "NEXUS_AI_TOUCH_RECEIPT.v2.9.0",
        "interaction_id": interaction_id,
        "provider": provider,
        "model_identifier": model_identifier,
        "session_id_hash": sha_text(session_id),
        "started_at_utc": utc(),
        "completed_at_utc": None,
        "status": "open",
        "human_intent": {"summary": redacted_intent, "intent_hash": sha_text(redacted_intent)},
        "pre_state": _pre_state(root_path),
        "post_state": None,
        "change_set": None,
        "validation": None,
        "human_disposition": "pending_review",
        "redaction_report": redaction,
        "prompt_injection_quarantine": quarantine_report(intent),
        "authority_boundary": {
            "interaction_is_evidence": True,
            "interaction_is_not_knowledge": True,
            "may_execute": False,
            "may_authorize": False,
            "may_calibrate_directly": False,
        },
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    write_json(root_path / STATE / interaction_id / "receipt.json", receipt)
    write_json(root_path / REPORT, receipt)
    append_hash_chained_event(root_path / LEDGER, {"event_type": "ai_touch_begin", "interaction_id": interaction_id, "receipt_hash": receipt["receipt_hash"]}, "ai-touch")
    return receipt


def end(root: str | Path, interaction_id: str, disposition: str) -> dict[str, Any]:
    if disposition not in VALID_DISPOSITIONS:
        raise ValueError("invalid_disposition")
    root_path = Path(root)
    path = root_path / STATE / interaction_id / "receipt.json"
    receipt = read_json(path, {})
    if not receipt:
        raise FileNotFoundError(interaction_id)
    files = changed_files(root_path)
    receipt.update(
        {
            "completed_at_utc": utc(),
            "status": "closed",
            "post_state": _pre_state(root_path),
            "change_set": {
                "patch_hash": patch_hash(root_path),
                "changed_files": files,
                "touched_python_symbols": _symbols(root_path, files),
                "touched_test_names": _test_names(root_path, files),
                "touched_schemas": [rel for rel in files if rel.startswith("schemas/")],
                "touched_command_ids": [rel for rel in files if rel.startswith("registry/") or rel.startswith("scripts/")],
                "commit_bound": git_commit(root_path),
                "committed": not bool(run_git(root_path, ["status", "--porcelain"])),
            },
            "validation": {
                "test_outputs": [],
                "evolve_output_reference": "not_recorded",
                "validation_evidence_hashes": [],
            },
            "human_disposition": disposition,
        }
    )
    receipt["receipt_hash"] = receipt_hash(receipt)
    write_json(path, receipt)
    write_json(root_path / REPORT, receipt)
    append_hash_chained_event(root_path / LEDGER, {"event_type": "ai_touch_end", "interaction_id": interaction_id, "receipt_hash": receipt["receipt_hash"], "disposition": disposition}, "ai-touch")
    return receipt


def abort(root: str | Path, interaction_id: str) -> dict[str, Any]:
    return end(root, interaction_id, "abandoned")


def status(root: str | Path, interaction_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root)
    if interaction_id:
        receipt = read_json(root_path / STATE / interaction_id / "receipt.json", {})
        return receipt or {"status": "missing", "interaction_id": interaction_id}
    receipts = [read_json(path, {}) for path in sorted((root_path / STATE).glob("*/receipt.json"))]
    return {"schema": "NEXUS_AI_TOUCH_STATUS.v2.9.0", "status": "pass", "open_interactions": [r["interaction_id"] for r in receipts if r.get("status") == "open"], "interaction_count": len(receipts)}


def verify(root: str | Path, interaction_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root)
    targets = [root_path / STATE / interaction_id / "receipt.json"] if interaction_id else sorted((root_path / STATE).glob("*/receipt.json"))
    failures: list[str] = []
    checked = 0
    for path in targets:
        receipt = read_json(path, {})
        if not receipt:
            failures.append(f"missing:{path}")
            continue
        checked += 1
        if receipt.get("receipt_hash") != receipt_hash(receipt):
            failures.append(f"receipt_hash_mismatch:{receipt.get('interaction_id')}")
        if receipt.get("human_disposition") not in VALID_DISPOSITIONS:
            failures.append(f"invalid_disposition:{receipt.get('interaction_id')}")
        if (receipt.get("redaction_report") or {}).get("status") != "pass":
            failures.append(f"redaction_failed:{receipt.get('interaction_id')}")
    chain = verify_hash_chain(root_path / LEDGER)
    if not chain["chain_valid"]:
        failures.append("ledger_chain_invalid")
    report = {
        "schema": "NEXUS_AI_TOUCH_VERIFY.v2.9.0",
        "status": "pass" if not failures else "fail",
        "checked_receipts": checked,
        "failures": failures,
        "ledger_chain": chain,
        "claim_boundary": "AI touch verification proves receipt integrity, not knowledge promotion.",
    }
    write_json(root_path / VERIFY_REPORT, report)
    return report


def replay_verify(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    chain = verify_hash_chain(root_path / LEDGER)
    receipts = sorted((root_path / STATE).glob("*/receipt.json"))
    report = {
        "schema": "NEXUS_AI_TOUCH_REPLAY.v2.9.0",
        "status": "pass" if chain["chain_valid"] else "fail",
        "ledger_chain": chain,
        "reconstructed_interactions": len(receipts),
        "runtime_state_replayable": True,
    }
    return report
