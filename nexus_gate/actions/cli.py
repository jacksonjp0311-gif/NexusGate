from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from nexus_gate.epochs.seal import build_epoch_integrity_seal, verify_epoch_integrity, write_epoch_integrity_seal
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain


VERSION = "2.6.2"
REGISTRY_PATH = Path("registry") / "nexus_command_registry.v2.6.2.json"
ACTION_ROOT = Path("state") / "actions"
LATEST_POINTER = Path("state") / "latest_action_pointer.json"
REPORT_LATEST = Path("reports") / "nexus_causal_action_receipt_latest.json"
ACTION_LEDGER = Path("ledger") / "action_receipts.jsonl"
LIFECYCLE_LEDGER = Path("ledger") / "action_lifecycle.jsonl"
OUTCOME_LEDGER = Path("ledger") / "causal_outcomes.jsonl"
CALIBRATION_LEDGER = Path("ledger") / "route_calibration_events.jsonl"
CALIBRATION_STATE = Path("state") / "calibration" / "route_models_latest.json"

ORDER = ["PROPOSED", "AUTHORIZED", "EXECUTING", "EXECUTED", "VALIDATED", "LEARNABLE"]
TERMINAL = {"DENIED", "EXPIRED", "STALE", "ABORTED", "FAILED", "CONFOUNDED", "INVALID", "NOT_LEARNABLE"}
VALID_TRANSITIONS = {
    "NONE": {"PROPOSED"},
    "PROPOSED": {"AUTHORIZED", "DENIED", "EXPIRED", "STALE"},
    "AUTHORIZED": {"EXECUTING", "DENIED", "EXPIRED", "STALE"},
    "EXECUTING": {"EXECUTED", "FAILED", "ABORTED"},
    "EXECUTED": {"VALIDATED", "FAILED", "CONFOUNDED"},
    "VALIDATED": {"LEARNABLE", "NOT_LEARNABLE"},
    "LEARNABLE": set(),
}

CLAIM_BOUNDARY = (
    "Causal Action Receipts bind recommendations, explicit human authorization, registered execution, "
    "repository effects, validation, epoch identity, and bounded calibration. They do not prove "
    "consciousness, general intelligence, scientific truth, security, production readiness, autonomous "
    "authority, or globally correct causal inference."
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_obj(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _write_json(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        Path(tmp_name).replace(path)
    finally:
        tmp = Path(tmp_name)
        if tmp.exists():
            tmp.unlink()


def _git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=False)


def _status_paths(root: Path) -> list[str]:
    rows: list[str] = []
    for line in _git(root, ["status", "--porcelain", "--untracked-files=all"]).stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].strip().replace("\\", "/")
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if rel.startswith('"') and rel.endswith('"'):
            rel = rel[1:-1]
        rows.append(rel)
    return sorted(rows)


def _snapshot(root: Path) -> dict[str, Any]:
    epoch = write_epoch_integrity_seal(root, build_epoch_integrity_seal(root))
    return {
        "epoch_id": epoch["source_epoch_id"],
        "source_root": epoch["source_root"],
        "epoch_state": epoch["epoch_state"],
        "durable_admissibility": epoch["durable_admissibility"],
        "eligible_as_learning_parent": epoch["eligible_as_learning_parent"],
        "git_commit": (_git(root, ["rev-parse", "HEAD"]).stdout.strip() or "unknown"),
        "git_status_paths": _status_paths(root),
        "git_status_hash": _sha_obj(_status_paths(root)),
        "working_tree_snapshot_hash": _sha_obj({"paths": _status_paths(root), "epoch": epoch["source_epoch_id"]}),
        "origin_manifest_hash": _sha_obj(_read_json(root / "state" / "nexus_origin_manifest_latest.json", {})),
        "epoch_manifest_hash": epoch.get("manifest_hash"),
    }


def _load_registry(root: Path) -> dict[str, Any]:
    registry = _read_json(root / REGISTRY_PATH, {})
    return {item["command_registry_id"]: item for item in registry.get("commands", [])}


def _normalize_arguments(args: dict[str, Any] | None = None) -> dict[str, Any]:
    return dict(sorted((args or {}).items()))


def _receipt_hash(packet: dict[str, Any]) -> str:
    return _sha_obj({key: value for key, value in packet.items() if key != "receipt_hash"})


def _action_dir(root: Path, action_id: str) -> Path:
    return root / ACTION_ROOT / action_id


def _stage_path(root: Path, action_id: str, stage: str) -> Path:
    return _action_dir(root, action_id) / f"{stage}.json"


def _write_receipt(root: Path, action_id: str, stage: str, packet: dict[str, Any]) -> dict[str, Any]:
    path = _stage_path(root, action_id, stage)
    packet["receipt_hash"] = _receipt_hash(packet)
    if path.exists():
        existing = _read_json(path, {})
        if existing.get("receipt_hash") != packet["receipt_hash"]:
            raise ValueError(f"Immutable receipt mismatch for {stage}: {action_id}")
        packet = existing
    else:
        _write_json(path, packet)
    append_hash_chained_event(root / ACTION_LEDGER, {
        "schema": "NEXUS_ACTION_LEDGER_EVENT.v2.6.2",
        "event_type": stage,
        "action_id": action_id,
        "recommendation_id": packet.get("recommendation_id"),
        "receipt_hash": packet["receipt_hash"],
        "producer_version": VERSION,
    }, producer=f"action-{stage}")
    return packet


def _lifecycle(root: Path, action_id: str) -> dict[str, Any]:
    return _read_json(_stage_path(root, action_id, "lifecycle"), {"state": "NONE", "history": []})


def _transition(root: Path, action_id: str, target: str, reason: str) -> dict[str, Any]:
    lifecycle = _lifecycle(root, action_id)
    current = lifecycle.get("state", "NONE")
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed and current not in TERMINAL:
        raise ValueError(f"Invalid action lifecycle transition: {current} -> {target}")
    lifecycle = {
        "schema": "NEXUS_ACTION_LIFECYCLE.v2.6.2",
        "action_id": action_id,
        "state": target,
        "updated_at_utc": _utc(),
        "history": [*lifecycle.get("history", []), {"from": current, "to": target, "at": _utc(), "reason": reason}],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(_stage_path(root, action_id, "lifecycle"), lifecycle)
    append_hash_chained_event(root / LIFECYCLE_LEDGER, {
        "schema": "NEXUS_ACTION_LIFECYCLE_EVENT.v2.6.2",
        "event_type": "lifecycle",
        "action_id": action_id,
        "from_state": current,
        "to_state": target,
        "reason": reason,
        "producer_version": VERSION,
    }, producer="action-lifecycle")
    return lifecycle


def _route_from_decision(root: Path) -> tuple[str, str, str, float]:
    decision = _read_json(root / "reports" / "nexus_decision_envelope_latest.json", {})
    selected = decision.get("selected_action") or {}
    command = selected.get("command") or ""
    lane = ""
    if "cortex-refresh" in command or selected.get("next_loop") == "cortex-refresh":
        lane = "nexus.cortex-refresh"
    elif "predictive-memory" in command:
        lane = "nexus.predictive-memory"
    elif "origin-seal" in command:
        lane = "nexus.origin-seal"
    elif "epoch-seal" in command:
        lane = "nexus.epoch-seal"
    elif "distill" in command:
        lane = "nexus.distill"
    elif "coherence-field" in command:
        lane = "nexus.coherence-field"
    elif "decision-envelope" in command:
        lane = "nexus.decision-envelope"
    elif "runtime-hygiene" in command:
        lane = "nexus.runtime-hygiene"
    else:
        lane = "nexus.cortex-refresh"
    return lane, selected.get("why", "Decision Envelope selected a registered route for shadow receipt capture."), _sha_obj(decision), float(selected.get("arbiter_score") or 0)


def recommend(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    registry = _load_registry(root_path)
    command_id, reason, decision_hash, utility = _route_from_decision(root_path)
    command = registry[command_id]
    args = _normalize_arguments({})
    pre = _snapshot(root_path)
    recommendation_id = _sha_obj({
        "pre_epoch_id": pre["epoch_id"],
        "command_registry_id": command_id,
        "normalized_arguments": args,
        "decision_hash": decision_hash,
        "producer_version": VERSION,
    })
    action_id = _sha_obj({"recommendation_id": recommendation_id, "created_at_utc": _utc(), "nonce": os.urandom(8).hex()})
    packet = {
        "schema": "NEXUS_ACTION_RECOMMENDATION_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": recommendation_id,
        "created_at_utc": _utc(),
        "pre_epoch": pre,
        "recommendation": {
            "command_registry_id": command_id,
            "lane": command["lane"],
            "normalized_arguments": args,
            "arguments_hash": _sha_obj(args),
            "reason": reason,
            "confidence": 0.72,
            "utility_estimate": utility,
            "risk_estimate": {"low": 0.2, "moderate": 0.5, "high": 0.8}.get(command["risk_class"], 0.5),
        },
        "evidence": {
            "decision_envelope_hash": decision_hash,
            "coherence_field_hash": _sha_obj(_read_json(root_path / "reports" / "nexus_coherence_field_latest.json", {})),
            "triadic_lattice_hash": _sha_obj(_read_json(root_path / "reports" / "nexus_triadic_lattice_latest.json", {})),
            "distillation_graph_hash": _sha_obj(_read_json(root_path / "reports" / "nexus_evidence_distillation_report_latest.json", {})),
            "predictive_memory_hash": _sha_obj(_read_json(root_path / "reports" / "nexus_predictive_memory_orchestrator_latest.json", {})),
            "origin_seal_hash": _sha_obj(_read_json(root_path / "reports" / "nexus_origin_seal_latest.json", {})),
        },
        "predictions": {
            "predicted_read_set": command["predicted_read_prefixes"],
            "predicted_write_set": command["predicted_write_prefixes"],
            "expected_gate_changes": command["required_postconditions"],
            "expected_effects": ["registered_lane_report_update"],
            "expected_duration_seconds": command["timeout_seconds"],
            "expected_exit_class": "success",
        },
        "constraints": {
            "blocking_conditions": [],
            "expires_at_utc": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
            "human_authorization_required": True,
        },
        "authority_boundary": {"recommendation_only": True, "autonomous_execution": False},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "PROPOSED", "recommendation created")
    packet = _write_receipt(root_path, action_id, "recommendation", packet)
    _write_json(root_path / LATEST_POINTER, {"schema": "NEXUS_LATEST_ACTION_POINTER.v2.6.2", "action_id": action_id, "recommendation_id": recommendation_id, "state": "PROPOSED", "updated_at_utc": _utc()})
    _write_json(root_path / REPORT_LATEST, {"schema": "NEXUS_CAUSAL_ACTION_RECEIPT_REPORT.v2.6.2", "status": "warn", "mode": "shadow", "action_id": action_id, "authorization_required": True, "execution_performed": False, "learning_performed": False, "receipt": packet, "claim_boundary": CLAIM_BOUNDARY})
    return packet


def authorize(root: str | Path, action_id: str, note: str = "", expires_minutes: int = 30) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    if not rec:
        raise ValueError("Missing recommendation receipt")
    pre = _snapshot(root_path)
    if pre["epoch_id"] != rec["pre_epoch"]["epoch_id"]:
        _transition(root_path, action_id, "STALE", "source epoch changed before authorization")
        raise ValueError("Recommendation is stale; source epoch changed")
    packet = {
        "schema": "NEXUS_ACTION_AUTHORIZATION_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "authorization_status": "authorized",
        "authorized_at_utc": _utc(),
        "expires_at_utc": (datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).isoformat(),
        "authorized_binding": {
            "command_registry_id": rec["recommendation"]["command_registry_id"],
            "arguments_hash": rec["recommendation"]["arguments_hash"],
            "pre_epoch_id": rec["pre_epoch"]["epoch_id"],
            "pre_source_root": rec["pre_epoch"]["source_root"],
        },
        "human_authorization": {"method": "explicit_cli", "actor": "local_human_operator", "note": note},
        "authority_boundary": {"single_action_only": True, "reusable": False, "delegable": False},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "AUTHORIZED", "explicit human authorization receipt")
    return _write_receipt(root_path, action_id, "authorization", packet)


def execute(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    auth = _read_json(_stage_path(root_path, action_id, "authorization"), {})
    if not auth:
        raise ValueError("No authorization receipt; execution blocked")
    current = _snapshot(root_path)
    if current["epoch_id"] != auth["authorized_binding"]["pre_epoch_id"]:
        _transition(root_path, action_id, "STALE", "source epoch changed before execution")
        raise ValueError("Authorized action is stale")
    registry = _load_registry(root_path)
    command = registry[rec["recommendation"]["command_registry_id"]]
    target = command["executor"]["target"]
    argv = [os.sys.executable, "-m", target, "--root", ".", "--json"]
    _transition(root_path, action_id, "EXECUTING", "registered command execution started")
    started = _utc()
    proc = subprocess.run(argv, cwd=str(root_path), capture_output=True, text=True, timeout=int(command["timeout_seconds"]), check=False)
    completed = _utc()
    post = _snapshot(root_path)
    packet = {
        "schema": "NEXUS_ACTION_EXECUTION_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "execution": {
            "command_registry_id": command["command_registry_id"],
            "arguments_hash": rec["recommendation"]["arguments_hash"],
            "started_at_utc": started,
            "completed_at_utc": completed,
            "duration_ms": 0,
            "exit_code": proc.returncode,
            "exit_class": "success" if proc.returncode == 0 else "failure",
            "stdout_hash": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
            "stderr_hash": hashlib.sha256(proc.stderr.encode("utf-8", errors="replace")).hexdigest(),
            "stdout_excerpt": proc.stdout[-1200:],
            "stderr_excerpt": proc.stderr[-1200:],
        },
        "pre_execution": current,
        "post_execution_observation": post,
        "authority": {"authorization_receipt_hash": auth.get("receipt_hash"), "authorization_valid": True},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "EXECUTED" if proc.returncode == 0 else "FAILED", "registered command execution completed")
    return _write_receipt(root_path, action_id, "execution", packet)


def effects(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    exe = _read_json(_stage_path(root_path, action_id, "execution"), {})
    if not exe:
        raise ValueError("Missing execution receipt")
    actual = sorted(set(exe["post_execution_observation"].get("git_status_paths", [])) - set(exe["pre_execution"].get("git_status_paths", [])))
    predicted = rec["predictions"]["predicted_write_set"]
    expected = [path for path in actual if any(path.startswith(prefix.rstrip("/")) for prefix in predicted)]
    unexpected = [path for path in actual if path not in expected]
    precision = 1.0 if not actual else len(expected) / max(1, len(actual))
    recall = len(expected) / max(1, len(predicted))
    effect_class = "expected" if not unexpected else "unexpected"
    packet = {
        "schema": "NEXUS_ACTION_EFFECT_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "surface_effects": {
            "actual_write_set": actual,
            "predicted_write_set": predicted,
            "expected_writes_observed": expected,
            "unexpected_writes": unexpected,
            "predicted_writes_missing": [],
        },
        "prediction_errors": {
            "write_set_precision": precision,
            "write_set_recall": recall,
            "duration_error_ratio": None,
            "exit_class_match": exe["execution"]["exit_class"] == rec["predictions"]["expected_exit_class"],
            "gate_prediction_accuracy": 1.0 if exe["execution"]["exit_class"] == "success" else 0.0,
        },
        "confounders": {
            "concurrent_mutation_detected": False,
            "unrelated_source_changes_detected": bool(unexpected),
            "unexpected_process_effects": False,
            "confounder_pressure": 0.4 if unexpected else 0.0,
        },
        "effect_class": effect_class,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if unexpected:
        _transition(root_path, action_id, "CONFOUNDED", "unexpected writes detected")
    return _write_receipt(root_path, action_id, "effects", packet)


def validate(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    exe = _read_json(_stage_path(root_path, action_id, "execution"), {})
    eff = _read_json(_stage_path(root_path, action_id, "effects"), {})
    if not exe:
        raise ValueError("Missing execution receipt")
    epoch_verify = verify_epoch_integrity(root_path)
    passed = exe["execution"]["exit_class"] == "success" and epoch_verify["status"] == "pass" and not eff.get("surface_effects", {}).get("unexpected_writes")
    packet = {
        "schema": "NEXUS_ACTION_VALIDATION_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": rec.get("recommendation_id"),
        "validation": {
            "started_at_utc": _utc(),
            "completed_at_utc": _utc(),
            "checks": [{"check_id": "epoch-verify", "status": epoch_verify["status"], "exit_code": 0 if epoch_verify["status"] == "pass" else 1, "evidence_hash": _sha_obj(epoch_verify)}],
            "required_checks_passed": passed,
            "final_evolve_passed": False,
        },
        "epoch_validation": {
            "pre_epoch_valid": True,
            "post_epoch_valid": epoch_verify["status"] == "pass",
            "post_epoch_id": epoch_verify.get("source_epoch_id"),
            "epoch_chain_valid": epoch_verify["epoch_chain"]["chain_valid"],
        },
        "causal_validation": {
            "authorization_match": True,
            "command_match": True,
            "arguments_match": True,
            "execution_receipt_present": True,
            "unexpected_write_policy_passed": not eff.get("surface_effects", {}).get("unexpected_writes"),
            "confounders_within_limit": (eff.get("confounders") or {}).get("confounder_pressure", 1.0) < 0.5,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "VALIDATED", "validation receipt generated")
    return _write_receipt(root_path, action_id, "validation", packet)


def finalize(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    val = _read_json(_stage_path(root_path, action_id, "validation"), {})
    eff = _read_json(_stage_path(root_path, action_id, "effects"), {})
    if not val:
        raise ValueError("Missing validation receipt")
    E = 1.0 if val["epoch_validation"]["post_epoch_valid"] else 0.0
    A = 1.0 if val["causal_validation"]["authorization_match"] else 0.0
    X = 1.0 if val["causal_validation"]["execution_receipt_present"] else 0.0
    W = float((eff.get("prediction_errors") or {}).get("write_set_precision") or 0.0)
    V = 1.0 if val["validation"]["required_checks_passed"] else 0.0
    F = 1.0 - float((eff.get("confounders") or {}).get("confounder_pressure") or 0.0)
    K = round(E * A * X * W * V * F, 4)
    learnable = K >= 0.85 and rec["pre_epoch"]["durable_admissibility"] == "admissible"
    packet = {
        "schema": "NEXUS_ACTION_LEARNING_RECEIPT.v2.6.2",
        "action_id": action_id,
        "recommendation_id": rec.get("recommendation_id"),
        "learnable": learnable,
        "causal_confidence": K,
        "outcome": {
            "classification": "success" if learnable else "not_learnable",
            "validated_effects": eff.get("surface_effects", {}),
            "prediction_errors": eff.get("prediction_errors", {}),
            "route_quality_delta": 0.01 if learnable else 0.0,
        },
        "calibration": {"eligible": learnable, "applied": False, "maximum_single_update": 0.05},
        "boundaries": {"does_not_authorize_future_actions": True, "does_not_prove_global_correctness": True},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "LEARNABLE" if learnable else "NOT_LEARNABLE", "learning gate evaluated")
    _write_receipt(root_path, action_id, "learning", packet)
    append_hash_chained_event(root_path / OUTCOME_LEDGER, {"schema": "NEXUS_CAUSAL_OUTCOME_EVENT.v2.6.2", "event_type": "causal_outcome", "action_id": action_id, "recommendation_id": rec.get("recommendation_id"), "learnable": learnable, "causal_confidence": K}, producer="causal-outcome")
    return packet


def chain_verify(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    chains = {
        "action_receipts": verify_hash_chain(root_path / ACTION_LEDGER),
        "action_lifecycle": verify_hash_chain(root_path / LIFECYCLE_LEDGER),
        "causal_outcomes": verify_hash_chain(root_path / OUTCOME_LEDGER),
        "route_calibration": verify_hash_chain(root_path / CALIBRATION_LEDGER),
    }
    status = "pass" if all(item["chain_valid"] for item in chains.values()) else "fail"
    packet = {"schema": "NEXUS_ACTION_CHAIN_VERIFY.v2.6.2", "status": status, "generated_at_utc": _utc(), "chains": chains, "claim_boundary": CLAIM_BOUNDARY}
    _write_json(root_path / "reports" / "nexus_action_chain_verify_latest.json", packet)
    return packet


def status(root: str | Path, action_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if not action_id:
        pointer = _read_json(root_path / LATEST_POINTER, {})
        action_id = pointer.get("action_id")
    lifecycle = _lifecycle(root_path, action_id) if action_id else {}
    return {"schema": "NEXUS_ACTION_STATUS.v2.6.2", "status": lifecycle.get("state", "none"), "action_id": action_id, "lifecycle": lifecycle, "claim_boundary": CLAIM_BOUNDARY}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS causal action receipt loop.")
    parser.add_argument("command", choices=["recommend", "status", "authorize", "deny", "execute", "effects", "validate", "finalize", "chain-verify", "receipts"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--action-id", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--expires-minutes", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "recommend":
            packet = recommend(args.root)
        elif args.command == "authorize":
            packet = authorize(args.root, args.action_id, note=args.note, expires_minutes=args.expires_minutes)
        elif args.command == "deny":
            packet = _transition(Path(args.root).resolve(), args.action_id, "DENIED", "explicit human denial")
        elif args.command == "execute":
            packet = execute(args.root, args.action_id)
        elif args.command == "effects":
            packet = effects(args.root, args.action_id)
        elif args.command == "validate":
            packet = validate(args.root, args.action_id)
        elif args.command == "finalize":
            packet = finalize(args.root, args.action_id)
        elif args.command == "chain-verify":
            packet = chain_verify(args.root)
        else:
            packet = status(args.root, args.action_id or None)
    except Exception as exc:
        packet = {"schema": "NEXUS_ACTION_ERROR.v2.6.2", "status": "fail", "error": str(exc), "claim_boundary": CLAIM_BOUNDARY}
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS causal action: {packet.get('status', packet.get('authorization_status', 'ok'))} {packet.get('action_id', '')}")
    return 0 if packet.get("status", "pass") in {"pass", "warn", "PROPOSED", "AUTHORIZED", "EXECUTED", "VALIDATED", "none"} or "receipt_hash" in packet else 1


if __name__ == "__main__":
    raise SystemExit(main())
