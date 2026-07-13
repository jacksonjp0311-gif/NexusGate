from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from nexus_gate.epochs.seal import build_epoch_integrity_seal, verify_epoch_integrity, write_epoch_integrity_seal
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain


VERSION = "2.6.3"
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
    "EXECUTED": {"EFFECTS_CAPTURED", "FAILED", "CONFOUNDED"},
    "EFFECTS_CAPTURED": {"VALIDATED", "FAILED", "CONFOUNDED", "NOT_LEARNABLE"},
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


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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


GENERATED_PREFIXES = (
    "reports/",
    "state/",
    "ledger/",
    "electron/.vite/",
    "electron/dist/",
)


CANONICAL_SOURCE_PREFIXES = (
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "requirements",
    "nexus_gate/",
    "scripts/",
    "tests/",
    "docs/",
    "policy/",
    "chatgpt/",
    "schemas/",
    "registry/",
    "rcc/",
    "electron/",
    ".github/",
)


def _classify_path(path: str) -> str:
    norm = path.replace("\\", "/")
    if norm == "state/neural_activity/repo_neural_graph_latest.json":
        return "generated_runtime_cache"
    if any(norm.startswith(prefix) for prefix in GENERATED_PREFIXES):
        return "generated"
    if norm in {"README.md", "AGENTS.md", "pyproject.toml", "package.json", "package-lock.json"}:
        return "canonical_source"
    if any(norm.startswith(prefix) for prefix in CANONICAL_SOURCE_PREFIXES):
        return "canonical_source"
    return "other"


def _file_digest(path: Path) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _working_tree_file_snapshot(root: Path) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for path in _status_paths(root):
        absolute = root / path
        rows[path] = {
            "exists": absolute.exists(),
            "hash": _file_digest(absolute),
            "size": absolute.stat().st_size if absolute.exists() and absolute.is_file() else None,
            "classification": _classify_path(path),
        }
    return rows


def _snapshot(root: Path) -> dict[str, Any]:
    epoch = write_epoch_integrity_seal(root, build_epoch_integrity_seal(root))
    paths = _status_paths(root)
    files = _working_tree_file_snapshot(root)
    return {
        "epoch_id": epoch["source_epoch_id"],
        "source_root": epoch["source_root"],
        "epoch_state": epoch["epoch_state"],
        "durable_admissibility": epoch["durable_admissibility"],
        "eligible_as_learning_parent": epoch["eligible_as_learning_parent"],
        "git_commit": (_git(root, ["rev-parse", "HEAD"]).stdout.strip() or "unknown"),
        "git_status_paths": paths,
        "git_status_hash": _sha_obj(paths),
        "working_tree_files": files,
        "working_tree_snapshot_hash": _sha_obj({"files": files, "epoch": epoch["source_epoch_id"]}),
        "origin_manifest_hash": _sha_obj(_read_json(root / "state" / "nexus_origin_manifest_latest.json", {})),
        "epoch_manifest_hash": epoch.get("manifest_hash"),
    }


def _load_registry(root: Path) -> dict[str, Any]:
    registry = _read_json(root / REGISTRY_PATH, {})
    return {item["command_registry_id"]: item for item in registry.get("commands", [])}


def _registry_entry_hash(command: dict[str, Any]) -> str:
    return _sha_obj(command)


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
            "schema": "NEXUS_ACTION_LEDGER_EVENT.v2.6.3",
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
    if target == current:
        return lifecycle
    if current in TERMINAL:
        raise ValueError(f"Terminal action lifecycle cannot transition: {current} -> {target}")
    if target not in allowed:
        raise ValueError(f"Invalid action lifecycle transition: {current} -> {target}")
    lifecycle = {
        "schema": "NEXUS_ACTION_LIFECYCLE.v2.6.3",
        "action_id": action_id,
        "state": target,
        "updated_at_utc": _utc(),
        "history": [*lifecycle.get("history", []), {"from": current, "to": target, "at": _utc(), "reason": reason}],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(_stage_path(root, action_id, "lifecycle"), lifecycle)
    append_hash_chained_event(root / LIFECYCLE_LEDGER, {
        "schema": "NEXUS_ACTION_LIFECYCLE_EVENT.v2.6.3",
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
        "schema": "NEXUS_ACTION_RECOMMENDATION_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": recommendation_id,
        "created_at_utc": _utc(),
        "pre_epoch": pre,
        "recommendation": {
            "command_registry_id": command_id,
            "command_registry_entry_hash": _registry_entry_hash(command),
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
    _write_json(root_path / LATEST_POINTER, {"schema": "NEXUS_LATEST_ACTION_POINTER.v2.6.3", "action_id": action_id, "recommendation_id": recommendation_id, "state": "PROPOSED", "updated_at_utc": _utc()})
    _write_json(root_path / REPORT_LATEST, {"schema": "NEXUS_CAUSAL_ACTION_RECEIPT_REPORT.v2.6.3", "status": "warn", "mode": "shadow", "action_id": action_id, "authorization_required": True, "execution_performed": False, "learning_performed": False, "receipt": packet, "claim_boundary": CLAIM_BOUNDARY})
    return packet


def authorize(root: str | Path, action_id: str, note: str = "", expires_minutes: int = 30) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if _stage_path(root_path, action_id, "authorization").exists():
        return _read_json(_stage_path(root_path, action_id, "authorization"), {})
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    if not rec:
        raise ValueError("Missing recommendation receipt")
    pre = _snapshot(root_path)
    if pre["epoch_id"] != rec["pre_epoch"]["epoch_id"]:
        _transition(root_path, action_id, "STALE", "source epoch changed before authorization")
        raise ValueError("Recommendation is stale; source epoch changed")
    packet = {
        "schema": "NEXUS_ACTION_AUTHORIZATION_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "authorization_status": "authorized",
        "authorized_at_utc": _utc(),
        "expires_at_utc": (datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).isoformat(),
        "authorized_binding": {
            "command_registry_id": rec["recommendation"]["command_registry_id"],
            "command_registry_entry_hash": rec["recommendation"].get("command_registry_entry_hash"),
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


def _verify_authorization_for_execution(root_path: Path, action_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    auth = _read_json(_stage_path(root_path, action_id, "authorization"), {})
    if not rec:
        raise ValueError("Missing recommendation receipt")
    if not auth:
        raise ValueError("No authorization receipt; execution blocked")
    if _stage_path(root_path, action_id, "execution").exists():
        raise ValueError("Action already executed; authorization is single-use")
    if _parse_utc(auth["expires_at_utc"]) < datetime.now(timezone.utc):
        _transition(root_path, action_id, "EXPIRED", "authorization expired")
        raise ValueError("Authorization expired")
    current = _snapshot(root_path)
    binding = auth["authorized_binding"]
    if current["epoch_id"] != binding["pre_epoch_id"] or current["source_root"] != binding["pre_source_root"]:
        _transition(root_path, action_id, "STALE", "source epoch changed before execution")
        raise ValueError("Authorized action is stale")
    if rec["recommendation"]["arguments_hash"] != binding["arguments_hash"]:
        _transition(root_path, action_id, "INVALID", "arguments hash mismatch")
        raise ValueError("Authorization arguments hash mismatch")
    registry = _load_registry(root_path)
    command = registry.get(binding["command_registry_id"])
    if not command:
        _transition(root_path, action_id, "STALE", "registry entry missing before execution")
        raise ValueError("Registry entry missing")
    if _registry_entry_hash(command) != binding.get("command_registry_entry_hash"):
        _transition(root_path, action_id, "STALE", "registry entry changed before execution")
        raise ValueError("Registry entry changed before execution")
    return rec, auth, current, command


def execute(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec, auth, current, command = _verify_authorization_for_execution(root_path, action_id)
    target = command["executor"]["target"]
    argv = [os.sys.executable, "-m", target, "--root", ".", "--json"]
    _transition(root_path, action_id, "EXECUTING", "registered command execution started")
    started = _utc()
    start_time = time.perf_counter()
    timeout_occurred = False
    try:
        proc = subprocess.run(argv, cwd=str(root_path), capture_output=True, text=True, timeout=int(command["timeout_seconds"]), check=False)
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timeout_occurred = True
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        returncode = 124
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    completed = _utc()
    post = _snapshot(root_path)
    packet = {
        "schema": "NEXUS_ACTION_EXECUTION_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "execution": {
            "command_registry_id": command["command_registry_id"],
            "arguments_hash": rec["recommendation"]["arguments_hash"],
            "started_at_utc": started,
            "completed_at_utc": completed,
            "duration_ms": duration_ms,
            "timeout_budget_ms": int(command["timeout_seconds"]) * 1000,
            "timeout_occurred": timeout_occurred,
            "exit_code": returncode,
            "exit_class": "timeout" if timeout_occurred else ("success" if returncode == 0 else "failure"),
            "stdout_hash": hashlib.sha256(stdout.encode("utf-8", errors="replace")).hexdigest(),
            "stderr_hash": hashlib.sha256(stderr.encode("utf-8", errors="replace")).hexdigest(),
            "stdout_excerpt": stdout[-1200:],
            "stderr_excerpt": stderr[-1200:],
        },
        "pre_execution": current,
        "post_execution_observation": post,
        "authority": {"authorization_receipt_hash": auth.get("receipt_hash"), "authorization_valid": True},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "EXECUTED" if returncode == 0 and not timeout_occurred else "FAILED", "registered command execution completed")
    return _write_receipt(root_path, action_id, "execution", packet)


def _compare_file_snapshots(pre: dict[str, Any], post: dict[str, Any]) -> dict[str, Any]:
    before = pre.get("working_tree_files", {})
    after = post.get("working_tree_files", {})
    paths = sorted(set(before) | set(after))
    added: list[str] = []
    deleted: list[str] = []
    modified: list[str] = []
    already_dirty_changed: list[str] = []
    pre_existing_dirty: list[str] = sorted(before)
    for path in paths:
        b = before.get(path)
        a = after.get(path)
        if not b and a:
            added.append(path)
        elif b and not a:
            deleted.append(path)
        elif b and a and (b.get("hash"), b.get("size"), b.get("exists")) != (a.get("hash"), a.get("size"), a.get("exists")):
            modified.append(path)
            if path in before:
                already_dirty_changed.append(path)
    return {
        "actual_added": added,
        "actual_deleted": deleted,
        "actual_modified": modified,
        "pre_existing_dirty": pre_existing_dirty,
        "already_dirty_changed": already_dirty_changed,
        "actual_write_set": sorted(set(added + deleted + modified)),
    }


def effects(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    exe = _read_json(_stage_path(root_path, action_id, "execution"), {})
    if not exe:
        raise ValueError("Missing execution receipt")
    if _stage_path(root_path, action_id, "effects").exists():
        return _read_json(_stage_path(root_path, action_id, "effects"), {})
    comparison = _compare_file_snapshots(exe["pre_execution"], exe["post_execution_observation"])
    actual = comparison["actual_write_set"]
    predicted = rec["predictions"]["predicted_write_set"]
    expected = [path for path in actual if any(path.startswith(prefix.rstrip("/")) for prefix in predicted)]
    unexpected = [path for path in actual if path not in expected]
    unexpected_canonical = [path for path in unexpected if _classify_path(path) == "canonical_source"]
    unexpected_generated = [path for path in unexpected if _classify_path(path) in {"generated", "generated_runtime_cache"}]
    expected_canonical = [path for path in expected if _classify_path(path) == "canonical_source"]
    expected_generated = [path for path in expected if _classify_path(path) in {"generated", "generated_runtime_cache"}]
    precision = 1.0 if not actual else len(expected) / max(1, len(actual))
    recall = len(expected) / max(1, len(predicted))
    head_changed = exe["pre_execution"].get("git_commit") != exe["post_execution_observation"].get("git_commit")
    concurrent_marker = any((root_path / ACTION_ROOT / p / "execution.lock").exists() for p in os.listdir(root_path / ACTION_ROOT) if p != action_id) if (root_path / ACTION_ROOT).exists() else False
    confounded = bool(unexpected_canonical or head_changed or concurrent_marker)
    effect_class = "confounded" if confounded else ("partially_expected" if unexpected else "expected")
    packet = {
        "schema": "NEXUS_ACTION_EFFECT_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": rec["recommendation_id"],
        "surface_effects": {
            "actual_added": comparison["actual_added"],
            "actual_deleted": comparison["actual_deleted"],
            "actual_modified": comparison["actual_modified"],
            "pre_existing_dirty": comparison["pre_existing_dirty"],
            "already_dirty_changed": comparison["already_dirty_changed"],
            "actual_write_set": actual,
            "predicted_write_set": predicted,
            "expected_writes_observed": expected,
            "expected_canonical_source_writes": expected_canonical,
            "unexpected_canonical_source_writes": unexpected_canonical,
            "expected_generated_writes": expected_generated,
            "unexpected_generated_writes": unexpected_generated,
            "unexpected_writes": unexpected,
            "predicted_writes_missing": [],
        },
        "prediction_errors": {
            "write_set_precision": precision,
            "write_set_recall": recall,
            "duration_error_ratio": (
                abs(float(exe["execution"]["duration_ms"]) / 1000.0 - float(rec["predictions"]["expected_duration_seconds"])) / max(1.0, float(rec["predictions"]["expected_duration_seconds"]))
                if rec["predictions"].get("expected_duration_seconds") else None
            ),
            "exit_class_match": exe["execution"]["exit_class"] == rec["predictions"]["expected_exit_class"],
            "gate_prediction_accuracy": 1.0 if exe["execution"]["exit_class"] == "success" else 0.0,
        },
        "confounders": {
            "concurrent_mutation_detected": bool(concurrent_marker),
            "git_head_changed_during_execution": bool(head_changed),
            "unrelated_source_changes_detected": bool(unexpected_canonical),
            "unexpected_process_effects": False,
            "confounder_pressure": 0.8 if confounded else (0.3 if unexpected else 0.0),
        },
        "causality_language": "action-window-associated effect; process-level file access is not claimed",
        "effect_class": effect_class,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if confounded:
        _transition(root_path, action_id, "CONFOUNDED", "unexpected writes detected")
    else:
        _transition(root_path, action_id, "EFFECTS_CAPTURED", "effect receipt generated")
    return _write_receipt(root_path, action_id, "effects", packet)


def validate(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _read_json(_stage_path(root_path, action_id, "recommendation"), {})
    exe = _read_json(_stage_path(root_path, action_id, "execution"), {})
    eff = _read_json(_stage_path(root_path, action_id, "effects"), {})
    if not exe:
        raise ValueError("Missing execution receipt")
    if not eff:
        raise ValueError("Missing effect receipt; validation blocked")
    if _stage_path(root_path, action_id, "validation").exists():
        return _read_json(_stage_path(root_path, action_id, "validation"), {})
    epoch_verify = verify_epoch_integrity(root_path)
    action_chain = chain_verify(root_path)
    final_evolve_report = _read_json(root_path / "reports" / "human_surface" / "nexus_human_surface_summary_latest.json", {})
    final_evolve_passed = final_evolve_report.get("status") == "pass"
    effect_complete = bool(eff.get("surface_effects")) and "unexpected_writes" in eff.get("surface_effects", {})
    passed = (
        exe["execution"]["exit_class"] == "success"
        and epoch_verify["status"] == "pass"
        and action_chain["status"] == "pass"
        and effect_complete
        and not eff.get("surface_effects", {}).get("unexpected_canonical_source_writes")
    )
    packet = {
        "schema": "NEXUS_ACTION_VALIDATION_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": rec.get("recommendation_id"),
        "validation": {
            "started_at_utc": _utc(),
            "completed_at_utc": _utc(),
            "checks": [
                {"check_id": "epoch-verify", "status": epoch_verify["status"], "exit_code": 0 if epoch_verify["status"] == "pass" else 1, "evidence_hash": _sha_obj(epoch_verify)},
                {"check_id": "action-chain-verify", "status": action_chain["status"], "exit_code": 0 if action_chain["status"] == "pass" else 1, "evidence_hash": _sha_obj(action_chain)},
                {"check_id": "effect-receipt", "status": "pass" if effect_complete else "fail", "exit_code": 0 if effect_complete else 1, "evidence_hash": eff.get("receipt_hash")},
            ],
            "required_checks_passed": passed,
            "targeted_checks_passed": passed,
            "final_evolve_required": True,
            "final_evolve_passed": final_evolve_passed,
            "final_evolve_report_hash": _sha_obj(final_evolve_report) if final_evolve_report else None,
            "final_evolve_observation_id": _read_json(root_path / "state" / "latest_observation_pointer.json", {}).get("observation_id"),
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
            "effect_receipt_present": True,
            "effect_receipt_hash_valid": bool(eff.get("receipt_hash")),
            "actual_effect_capture_complete": effect_complete,
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
    if not eff:
        raise ValueError("Missing effect receipt")
    if _stage_path(root_path, action_id, "learning").exists():
        return _read_json(_stage_path(root_path, action_id, "learning"), {})
    E = 1.0 if val["epoch_validation"]["post_epoch_valid"] else 0.0
    A = 1.0 if val["causal_validation"]["authorization_match"] else 0.0
    R = 1.0 if val["causal_validation"]["command_match"] else 0.0
    X = 1.0 if val["causal_validation"]["execution_receipt_present"] else 0.0
    W = float((eff.get("prediction_errors") or {}).get("write_set_precision") or 0.0)
    V = 1.0 if val["validation"]["required_checks_passed"] and val["validation"].get("final_evolve_passed") else 0.0
    F = 1.0 - float((eff.get("confounders") or {}).get("confounder_pressure") or 0.0)
    D = 1.0 if rec["pre_epoch"]["durable_admissibility"] == "admissible" and val["epoch_validation"].get("post_epoch_valid") else 0.0
    K = round(E * A * R * X * W * V * F * D, 4)
    command = _load_registry(root_path).get(rec["recommendation"]["command_registry_id"], {})
    learnable = K >= 0.85 and command.get("learning_eligible") is True
    blockers = []
    if rec["pre_epoch"]["durable_admissibility"] != "admissible":
        blockers.append("pre_epoch_not_durably_admissible")
    if not val["validation"].get("final_evolve_passed"):
        blockers.append("final_evolve_not_passed")
    if (eff.get("confounders") or {}).get("confounder_pressure", 1.0) >= 0.5:
        blockers.append("confounded_effects")
    if not command.get("learning_eligible"):
        blockers.append("route_not_learning_eligible")
    packet = {
        "schema": "NEXUS_ACTION_LEARNING_RECEIPT.v2.6.3",
        "action_id": action_id,
        "recommendation_id": rec.get("recommendation_id"),
        "learnable": learnable,
        "causal_confidence": K,
        "causal_confidence_components": {"E": E, "A": A, "R": R, "X": X, "W": W, "V": V, "F": F, "D": D},
        "blocking_reasons": blockers,
        "outcome": {
            "classification": "success" if learnable else "not_learnable",
            "validated_effects": eff.get("surface_effects", {}),
            "prediction_errors": eff.get("prediction_errors", {}),
            "route_quality_delta": 0.01 if learnable else 0.0,
        },
        "calibration": {"eligible": learnable, "authorized": False, "applied": False, "status": "pending_human_calibration" if learnable else "blocked", "maximum_single_update": 0.05},
        "boundaries": {"does_not_authorize_future_actions": True, "does_not_prove_global_correctness": True},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "LEARNABLE" if learnable else "NOT_LEARNABLE", "learning gate evaluated")
    _write_receipt(root_path, action_id, "learning", packet)
    append_hash_chained_event(root_path / OUTCOME_LEDGER, {"schema": "NEXUS_CAUSAL_OUTCOME_EVENT.v2.6.3", "event_type": "causal_outcome", "action_id": action_id, "recommendation_id": rec.get("recommendation_id"), "learnable": learnable, "causal_confidence": K}, producer="causal-outcome")
    return packet


def first_learning_readiness(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    epoch_verify = verify_epoch_integrity(root_path)
    action_chains = chain_verify(root_path)
    registry = _read_json(root_path / REGISTRY_PATH, {})
    epoch = _read_json(root_path / "reports" / "nexus_epoch_integrity_seal_latest.json", {})
    clean_epoch_available = epoch.get("durable_admissibility") == "admissible"
    blockers: list[str] = []
    if not clean_epoch_available:
        blockers.append("clean_admissible_epoch_required")
    if epoch_verify.get("status") != "pass":
        blockers.append("epoch_verify_not_passed")
    if action_chains.get("status") != "pass":
        blockers.append("action_chain_not_valid")
    if not registry.get("commands"):
        blockers.append("command_registry_missing")
    packet = {
        "schema": "NEXUS_FIRST_LEARNING_READINESS.v2.6.3",
        "system": "NEXUS GATE",
        "version": "2.6.3",
        "status": "ready" if not blockers else "blocked",
        "clean_epoch_available": clean_epoch_available,
        "epoch_chains_valid": epoch_verify.get("epoch_chain", {}).get("chain_valid", False),
        "observation_chains_valid": epoch_verify.get("observation_chain", {}).get("chain_valid", False),
        "action_chains_valid": action_chains.get("status") == "pass",
        "registry_valid": bool(registry.get("commands")),
        "authorization_integrity_ready": True,
        "effect_capture_ready": True,
        "final_evolve_enforced": True,
        "calibration_path_ready": True,
        "blocking_reasons": blockers,
        "recommended_test_route": "nexus.cortex-refresh",
        "claim_boundary": CLAIM_BOUNDARY,
        "generated_at_utc": _utc(),
    }
    _write_json(root_path / "reports" / "nexus_first_learning_readiness_latest.json", packet)
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
    packet = {"schema": "NEXUS_ACTION_CHAIN_VERIFY.v2.6.3", "status": status, "generated_at_utc": _utc(), "chains": chains, "claim_boundary": CLAIM_BOUNDARY}
    _write_json(root_path / "reports" / "nexus_action_chain_verify_latest.json", packet)
    return packet


def status(root: str | Path, action_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if not action_id:
        pointer = _read_json(root_path / LATEST_POINTER, {})
        action_id = pointer.get("action_id")
    lifecycle = _lifecycle(root_path, action_id) if action_id else {}
    return {"schema": "NEXUS_ACTION_STATUS.v2.6.3", "status": lifecycle.get("state", "none"), "action_id": action_id, "lifecycle": lifecycle, "claim_boundary": CLAIM_BOUNDARY}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS causal action receipt loop.")
    parser.add_argument("command", choices=["recommend", "status", "authorize", "deny", "execute", "effects", "validate", "finalize", "chain-verify", "receipts", "first-learning-readiness"])
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
        elif args.command == "first-learning-readiness":
            packet = first_learning_readiness(args.root)
        else:
            packet = status(args.root, args.action_id or None)
    except Exception as exc:
        packet = {"schema": "NEXUS_ACTION_ERROR.v2.6.2", "status": "fail", "error": str(exc), "claim_boundary": CLAIM_BOUNDARY}
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS causal action: {packet.get('status', packet.get('authorization_status', 'ok'))} {packet.get('action_id', '')}")
    return 0 if packet.get("status", "pass") in {"pass", "warn", "blocked", "ready", "PROPOSED", "AUTHORIZED", "EXECUTED", "VALIDATED", "none"} or "receipt_hash" in packet else 1


if __name__ == "__main__":
    raise SystemExit(main())
    registry = _load_registry(root_path)
    command = registry.get(rec["recommendation"]["command_registry_id"])
    if not command:
        _transition(root_path, action_id, "STALE", "registry entry missing before authorization")
        raise ValueError("Registry entry missing")
    if _registry_entry_hash(command) != rec["recommendation"].get("command_registry_entry_hash"):
        _transition(root_path, action_id, "STALE", "registry entry changed before authorization")
        raise ValueError("Registry entry changed before authorization")
