from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from nexus_gate.epochs.seal import build_epoch_integrity_seal, verify_epoch_integrity, write_epoch_integrity_seal
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain


VERSION = "2.7.0"
REGISTRY_PATH = Path("registry") / "nexus_command_registry.v2.6.2.json"
ACTION_ROOT = Path("state") / "actions"
LATEST_POINTER = Path("state") / "latest_action_pointer.json"
LATEST_COMPLETED_POINTER = Path("state") / "latest_completed_action_pointer.json"
LATEST_EXPERIENCE_POINTER = Path("state") / "latest_verified_experience_pointer.json"
REPORT_LATEST = Path("reports") / "nexus_causal_action_receipt_latest.json"
ACTION_LEDGER = Path("ledger") / "action_receipts.jsonl"
LIFECYCLE_LEDGER = Path("ledger") / "action_lifecycle.jsonl"
OUTCOME_LEDGER = Path("ledger") / "causal_outcomes.jsonl"
CALIBRATION_LEDGER = Path("ledger") / "route_calibration_events.jsonl"
EXPERIENCE_LEDGER = Path("ledger") / "experience_chain.jsonl"
CALIBRATION_STATE = Path("state") / "calibration" / "route_models_latest.json"
EXECUTION_LOCK = ACTION_ROOT / "execution.lock"

ORDER = ["PROPOSED", "AUTHORIZED", "EXECUTING", "EXECUTED", "EFFECTS_CAPTURED", "VALIDATION_RECORDED", "VALIDATED_PASS", "LEARNABLE", "EXPERIENCE_SEALED", "CALIBRATION_PENDING", "CALIBRATED"]
TERMINAL = {"DENIED", "EXPIRED", "STALE", "ABORTED", "FAILED", "CONFOUNDED", "INVALID", "NOT_LEARNABLE", "CALIBRATED"}
VALID_TRANSITIONS = {
    "NONE": {"PROPOSED"},
    "PROPOSED": {"AUTHORIZED", "DENIED", "EXPIRED", "STALE"},
    "AUTHORIZED": {"EXECUTING", "DENIED", "EXPIRED", "STALE"},
    "EXECUTING": {"EXECUTED", "FAILED", "ABORTED"},
    "EXECUTED": {"EFFECTS_CAPTURED", "FAILED", "CONFOUNDED"},
    "EFFECTS_CAPTURED": {"VALIDATION_RECORDED", "FAILED", "CONFOUNDED", "NOT_LEARNABLE"},
    "VALIDATION_RECORDED": {"VALIDATED_PASS", "VALIDATED_FAIL", "NOT_LEARNABLE"},
    "VALIDATED_PASS": {"LEARNABLE", "NOT_LEARNABLE"},
    "VALIDATED_FAIL": {"NOT_LEARNABLE"},
    "LEARNABLE": {"EXPERIENCE_SEALED", "CALIBRATION_PENDING"},
    "EXPERIENCE_SEALED": {"CALIBRATION_PENDING"},
    "CALIBRATION_PENDING": {"CALIBRATED", "NOT_LEARNABLE"},
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


def _verify_receipt(root: Path, action_id: str, stage: str) -> dict[str, Any]:
    path = _stage_path(root, action_id, stage)
    packet = _read_json(path, {})
    checks: list[dict[str, Any]] = []
    if not packet:
        return {"stage": stage, "valid": False, "path": str(path), "checks": [{"check": "receipt_present", "status": "fail"}], "packet": {}}
    expected_hash = _receipt_hash(packet)
    checks.append({"check": "receipt_hash", "status": "pass" if packet.get("receipt_hash") == expected_hash else "fail", "expected": expected_hash, "actual": packet.get("receipt_hash")})
    checks.append({"check": "action_id", "status": "pass" if packet.get("action_id") == action_id else "fail"})
    schema = str(packet.get("schema") or "")
    checks.append({"check": "schema", "status": "pass" if schema.startswith("NEXUS_ACTION_") or schema.startswith("NEXUS_EXPERIENCE_") else "fail", "schema": schema})
    ledger = verify_hash_chain(root / ACTION_LEDGER)
    events = []
    try:
        for line in (root / ACTION_LEDGER).read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                events.append(json.loads(line))
    except FileNotFoundError:
        pass
    event_present = any(
        event.get("action_id") == action_id
        and event.get("event_type") == stage
        and event.get("receipt_hash") == packet.get("receipt_hash")
        for event in events
    )
    checks.append({"check": "ledger_event_present", "status": "pass" if event_present else "fail"})
    checks.append({"check": "ledger_hash_chain", "status": "pass" if ledger.get("chain_valid") else "fail"})
    return {"stage": stage, "valid": all(check["status"] == "pass" for check in checks), "path": str(path), "checks": checks, "packet": packet}


def _require_verified_receipt(root: Path, action_id: str, stage: str) -> dict[str, Any]:
    result = _verify_receipt(root, action_id, stage)
    if not result["valid"]:
        _transition(root, action_id, "INVALID", f"{stage} receipt failed verification")
        raise ValueError(f"{stage} receipt failed verification")
    return result["packet"]


def _receipt_ref(root: Path, action_id: str, stage: str) -> dict[str, Any]:
    result = _verify_receipt(root, action_id, stage)
    packet = result.get("packet") or {}
    return {
        "stage": stage,
        "valid": result["valid"],
        "path": str(_stage_path(root, action_id, stage).relative_to(root)),
        "receipt_hash": packet.get("receipt_hash"),
        "schema": packet.get("schema"),
    }


@contextmanager
def _execution_lock(root: Path, action_id: str):
    lock_path = root / EXECUTION_LOCK
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "NEXUS_ACTION_EXECUTION_LOCK.v2.7.0", "action_id": action_id, "pid": os.getpid(), "created_at_utc": _utc(), "created_at_epoch": time.time()}
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        existing = _read_json(lock_path, {})
        stale = (time.time() - float(existing.get("created_at_epoch", 0))) > 600
        if not stale:
            raise ValueError(f"Another governed action is executing: {existing.get('action_id')}")
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            handle.flush()
            os.fsync(handle.fileno())
        yield payload
    finally:
        try:
            current = _read_json(lock_path, {})
            if current.get("action_id") == action_id:
                lock_path.unlink()
        except FileNotFoundError:
            pass


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
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    if not rec:
        raise ValueError("Missing recommendation receipt")
    if _parse_utc(rec["constraints"]["expires_at_utc"]) < datetime.now(timezone.utc):
        _transition(root_path, action_id, "EXPIRED", "recommendation expired before authorization")
        raise ValueError("Recommendation expired")
    registry = _load_registry(root_path)
    command = registry.get(rec["recommendation"]["command_registry_id"])
    if not command:
        _transition(root_path, action_id, "STALE", "registry entry missing before authorization")
        raise ValueError("Registry entry missing")
    if _registry_entry_hash(command) != rec["recommendation"].get("command_registry_entry_hash"):
        _transition(root_path, action_id, "STALE", "registry entry changed before authorization")
        raise ValueError("Registry entry changed before authorization")
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
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    auth = _require_verified_receipt(root_path, action_id, "authorization")
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
    with _execution_lock(root_path, action_id) as lock:
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
        "authority": {"authorization_receipt_hash": auth.get("receipt_hash"), "authorization_valid": True, "execution_lock": lock},
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
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    exe = _require_verified_receipt(root_path, action_id, "execution")
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
    concurrent_marker = (root_path / EXECUTION_LOCK).exists()
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


def action_final_evolve(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    exe = _require_verified_receipt(root_path, action_id, "execution")
    eff = _require_verified_receipt(root_path, action_id, "effects")
    if _stage_path(root_path, action_id, "final_evolve").exists():
        return _read_json(_stage_path(root_path, action_id, "final_evolve"), {})
    started = _utc()
    epoch_verify = verify_epoch_integrity(root_path)
    chain = chain_verify(root_path)
    completed = _utc()
    post = _snapshot(root_path)
    canonical_source_unchanged = exe["post_execution_observation"].get("source_root") == post.get("source_root")
    checks = [
        {"check_id": "epoch-verify", "status": epoch_verify.get("status"), "evidence_hash": _sha_obj(epoch_verify)},
        {"check_id": "action-chain-verify", "status": chain.get("status"), "evidence_hash": _sha_obj(chain)},
        {"check_id": "effect-receipt", "status": "pass" if eff.get("receipt_hash") else "fail", "evidence_hash": eff.get("receipt_hash")},
        {"check_id": "canonical-source-unchanged-by-verifier", "status": "pass" if canonical_source_unchanged else "fail", "evidence_hash": post.get("source_root")},
    ]
    passed = all(check["status"] == "pass" for check in checks)
    packet = {
        "schema": "NEXUS_ACTION_FINAL_EVOLVE_RECEIPT.v2.7.0",
        "action_id": action_id,
        "recommendation_id": rec.get("recommendation_id"),
        "verification": {
            "verification_run_id": _sha_obj({"action_id": action_id, "started": started, "kind": "action-bound-final-evolve"}),
            "started_at_utc": started,
            "completed_at_utc": completed,
            "input_receipt_hashes": {
                "recommendation": rec.get("receipt_hash"),
                "authorization": _read_json(_stage_path(root_path, action_id, "authorization"), {}).get("receipt_hash"),
                "execution": exe.get("receipt_hash"),
                "effects": eff.get("receipt_hash"),
            },
            "post_action_observation_id": _read_json(root_path / "state" / "latest_observation_pointer.json", {}).get("observation_id"),
            "checks": checks,
            "checks_passed": passed,
            "canonical_source_unchanged": canonical_source_unchanged,
            "action_chain_valid": chain.get("status") == "pass",
            "epoch_chain_valid": epoch_verify.get("epoch_chain", {}).get("chain_valid", False),
            "experience_chain_valid": verify_hash_chain(root_path / EXPERIENCE_LEDGER).get("chain_valid", True),
        },
        "verifier_effect_boundary": "This receipt verifies the action after effect capture. Verifier-generated reports are not attributed to the target action.",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    packet = _write_receipt(root_path, action_id, "final_evolve", packet)
    _write_json(root_path / "reports" / "nexus_action_final_evolve_latest.json", packet)
    return packet


def validate(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    auth = _require_verified_receipt(root_path, action_id, "authorization")
    exe = _require_verified_receipt(root_path, action_id, "execution")
    eff = _require_verified_receipt(root_path, action_id, "effects")
    if _stage_path(root_path, action_id, "validation").exists():
        return _read_json(_stage_path(root_path, action_id, "validation"), {})
    epoch_verify = verify_epoch_integrity(root_path)
    action_chain = chain_verify(root_path)
    final_evolve_report = _read_json(_stage_path(root_path, action_id, "final_evolve"), {})
    final_evolve_passed = final_evolve_report.get("verification", {}).get("checks_passed") is True
    effect_complete = bool(eff.get("surface_effects")) and "unexpected_writes" in eff.get("surface_effects", {})
    binding = auth.get("authorized_binding", {})
    registry = _load_registry(root_path)
    command = registry.get(binding.get("command_registry_id"), {})
    authorization_match = auth.get("recommendation_id") == rec.get("recommendation_id")
    command_match = command.get("command_registry_id") == rec["recommendation"]["command_registry_id"]
    registry_match = command and _registry_entry_hash(command) == binding.get("command_registry_entry_hash")
    arguments_match = rec["recommendation"]["arguments_hash"] == binding.get("arguments_hash") == exe["execution"]["arguments_hash"]
    passed = (
        exe["execution"]["exit_class"] == "success"
        and epoch_verify["status"] == "pass"
        and action_chain["status"] == "pass"
        and effect_complete
        and not eff.get("surface_effects", {}).get("unexpected_canonical_source_writes")
        and final_evolve_passed
        and authorization_match
        and command_match
        and registry_match
        and arguments_match
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
                {"check_id": "action-bound-final-evolve", "status": "pass" if final_evolve_passed else "fail", "exit_code": 0 if final_evolve_passed else 1, "evidence_hash": final_evolve_report.get("receipt_hash")},
            ],
            "required_checks_passed": passed,
            "targeted_checks_passed": passed,
            "final_evolve_required": True,
            "final_evolve_passed": final_evolve_passed,
            "final_evolve_report_hash": final_evolve_report.get("receipt_hash"),
            "final_evolve_observation_id": final_evolve_report.get("verification", {}).get("post_action_observation_id"),
        },
        "epoch_validation": {
            "pre_epoch_valid": rec["pre_epoch"].get("epoch_id") == auth["authorized_binding"].get("pre_epoch_id"),
            "post_epoch_valid": epoch_verify["status"] == "pass",
            "post_epoch_durable_admissibility": epoch_verify.get("durable_admissibility"),
            "post_epoch_id": epoch_verify.get("source_epoch_id"),
            "epoch_chain_valid": epoch_verify["epoch_chain"]["chain_valid"],
        },
        "causal_validation": {
            "authorization_match": authorization_match,
            "command_match": bool(command_match and registry_match),
            "arguments_match": arguments_match,
            "execution_receipt_present": _verify_receipt(root_path, action_id, "execution")["valid"],
            "effect_receipt_present": bool(eff),
            "effect_receipt_hash_valid": _verify_receipt(root_path, action_id, "effects")["valid"],
            "actual_effect_capture_complete": effect_complete,
            "unexpected_write_policy_passed": not eff.get("surface_effects", {}).get("unexpected_writes"),
            "confounders_within_limit": (eff.get("confounders") or {}).get("confounder_pressure", 1.0) < 0.5,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _transition(root_path, action_id, "VALIDATION_RECORDED", "validation receipt generated")
    _transition(root_path, action_id, "VALIDATED_PASS" if passed else "VALIDATED_FAIL", "validation result classified")
    return _write_receipt(root_path, action_id, "validation", packet)


def finalize(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    rec = _require_verified_receipt(root_path, action_id, "recommendation")
    val = _require_verified_receipt(root_path, action_id, "validation")
    eff = _require_verified_receipt(root_path, action_id, "effects")
    if _stage_path(root_path, action_id, "learning").exists():
        return _read_json(_stage_path(root_path, action_id, "learning"), {})
    E = 1.0 if val["epoch_validation"]["pre_epoch_valid"] and val["epoch_validation"]["post_epoch_valid"] else 0.0
    A = 1.0 if val["causal_validation"]["authorization_match"] else 0.0
    R = 1.0 if val["causal_validation"]["command_match"] else 0.0
    X = 1.0 if val["causal_validation"]["execution_receipt_present"] else 0.0
    W = float((eff.get("prediction_errors") or {}).get("write_set_precision") or 0.0)
    V = 1.0 if val["validation"]["required_checks_passed"] and val["validation"].get("final_evolve_passed") else 0.0
    F = 1.0 - float((eff.get("confounders") or {}).get("confounder_pressure") or 0.0)
    D = 1.0 if (
        rec["pre_epoch"]["durable_admissibility"] == "admissible"
        and val["epoch_validation"].get("post_epoch_durable_admissibility") == "admissible"
    ) else 0.0
    K = round(E * A * R * X * W * V * F * D, 4)
    command = _load_registry(root_path).get(rec["recommendation"]["command_registry_id"], {})
    learnable = K >= 0.85 and command.get("learning_eligible") is True
    blockers = []
    if rec["pre_epoch"]["durable_admissibility"] != "admissible":
        blockers.append("pre_epoch_not_durably_admissible")
    if val["epoch_validation"].get("post_epoch_durable_admissibility") != "admissible":
        blockers.append("post_epoch_not_durably_admissible")
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
    latest_action = _read_json(root_path / LATEST_POINTER, {}).get("action_id")
    semantic = semantic_verify(root_path, latest_action) if latest_action else {"status": "pass", "reason": "no_action_yet"}
    experience_chain = experience_chain_verify(root_path)
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
        "schema": "NEXUS_EXPERIENCE_READINESS.v2.7.0",
        "system": "NEXUS GATE",
        "version": "2.7.0",
        "status": "ready" if not blockers else "blocked",
        "clean_epoch_available": clean_epoch_available,
        "epoch_chains_valid": epoch_verify.get("epoch_chain", {}).get("chain_valid", False),
        "observation_chains_valid": epoch_verify.get("observation_chain", {}).get("chain_valid", False),
        "action_chains_valid": action_chains.get("status") == "pass",
        "semantic_action_chain_valid": semantic.get("status") == "pass",
        "experience_chain_valid": experience_chain.get("status") == "pass",
        "registry_valid": bool(registry.get("commands")),
        "authorization_integrity_ready": callable(_verify_authorization_for_execution),
        "effect_capture_ready": callable(effects),
        "action_bound_final_evolve_available": callable(action_final_evolve),
        "final_evolve_enforced": True,
        "calibration_path_ready": callable(calibration_status),
        "execution_lock_protocol_ready": (root_path / ACTION_ROOT).exists() or (root_path / ACTION_ROOT).parent.exists(),
        "blocking_reasons": blockers,
        "recommended_test_route": "nexus.cortex-refresh",
        "claim_boundary": CLAIM_BOUNDARY,
        "generated_at_utc": _utc(),
    }
    _write_json(root_path / "reports" / "nexus_first_learning_readiness_latest.json", packet)
    _write_json(root_path / "reports" / "nexus_experience_readiness_latest.json", packet)
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


def semantic_verify(root: str | Path, action_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if not action_id:
        action_id = _read_json(root_path / LATEST_POINTER, {}).get("action_id")
    if not action_id:
        packet = {"schema": "NEXUS_ACTION_SEMANTIC_VERIFY.v2.7.0", "status": "pass", "reason": "no_action_yet", "claim_boundary": CLAIM_BOUNDARY}
        _write_json(root_path / "reports" / "nexus_action_semantic_verify_latest.json", packet)
        return packet
    stages = ["recommendation", "authorization", "execution", "effects", "final_evolve", "validation", "learning"]
    stage_results = [_verify_receipt(root_path, action_id, stage) for stage in stages if _stage_path(root_path, action_id, stage).exists()]
    by_stage = {item["stage"]: item for item in stage_results}
    failures: list[str] = []
    for result in stage_results:
        if not result["valid"]:
            failures.append(f"{result['stage']}_receipt_invalid")
    order = {stage: idx for idx, stage in enumerate(stages)}
    present_order = [order[item["stage"]] for item in stage_results]
    if present_order != sorted(present_order):
        failures.append("receipt_stage_order_invalid")
    if "authorization" in by_stage and "recommendation" not in by_stage:
        failures.append("authorization_without_recommendation")
    if "execution" in by_stage and "authorization" not in by_stage:
        failures.append("execution_without_authorization")
    if "effects" in by_stage and "execution" not in by_stage:
        failures.append("effects_without_execution")
    if "validation" in by_stage and ("effects" not in by_stage or "final_evolve" not in by_stage):
        failures.append("validation_without_effects_or_final_evolve")
    if "learning" in by_stage and "validation" not in by_stage:
        failures.append("learning_without_validation")
    rec = by_stage.get("recommendation", {}).get("packet") or {}
    recommendation_id = rec.get("recommendation_id")
    for result in stage_results:
        packet = result.get("packet") or {}
        if packet.get("recommendation_id") and recommendation_id and packet.get("recommendation_id") != recommendation_id:
            failures.append(f"{result['stage']}_recommendation_id_mismatch")
    lifecycle = _lifecycle(root_path, action_id)
    packet = {
        "schema": "NEXUS_ACTION_SEMANTIC_VERIFY.v2.7.0",
        "status": "pass" if not failures else "fail",
        "action_id": action_id,
        "lifecycle_state": lifecycle.get("state"),
        "verified_stages": [_receipt_ref(root_path, action_id, stage) for stage in stages if _stage_path(root_path, action_id, stage).exists()],
        "failures": failures,
        "claim_boundary": CLAIM_BOUNDARY,
        "generated_at_utc": _utc(),
    }
    _write_json(root_path / "reports" / "nexus_action_semantic_verify_latest.json", packet)
    return packet


def experience_chain_verify(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    chain = verify_hash_chain(root_path / EXPERIENCE_LEDGER)
    status = "pass" if chain.get("chain_valid") else "fail"
    packet = {"schema": "NEXUS_EXPERIENCE_CHAIN_VERIFY.v2.7.0", "status": status, "generated_at_utc": _utc(), "chain": chain, "claim_boundary": CLAIM_BOUNDARY}
    _write_json(root_path / "reports" / "nexus_experience_chain_verify_latest.json", packet)
    return packet


def experience_seal(root: str | Path, action_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    semantic = semantic_verify(root_path, action_id)
    if semantic.get("status") != "pass":
        return {"schema": "NEXUS_EXPERIENCE_SEAL.v2.7.0", "status": "blocked", "action_id": action_id, "blocking_reasons": semantic.get("failures", []), "claim_boundary": CLAIM_BOUNDARY}
    required = ["recommendation", "authorization", "execution", "effects", "final_evolve", "validation", "learning"]
    refs = {stage: _receipt_ref(root_path, action_id, stage) for stage in required if _stage_path(root_path, action_id, stage).exists()}
    missing = [stage for stage in required if stage not in refs]
    if missing:
        return {"schema": "NEXUS_EXPERIENCE_SEAL.v2.7.0", "status": "blocked", "action_id": action_id, "blocking_reasons": [f"missing_{stage}" for stage in missing], "claim_boundary": CLAIM_BOUNDARY}
    exp_id = _sha_obj({"action_id": action_id, "source_epoch_id": _read_json(_stage_path(root_path, action_id, "recommendation"), {}).get("pre_epoch", {}).get("epoch_id"), "refs": refs})
    exp_dir = root_path / "state" / "experiences" / exp_id
    manifest = {
        "schema": "NEXUS_EXPERIENCE_SEAL.v2.7.0",
        "experience_id": exp_id,
        "action_id": action_id,
        "status": "sealed",
        "source_epoch_id": _read_json(_stage_path(root_path, action_id, "recommendation"), {}).get("pre_epoch", {}).get("epoch_id"),
        "receipt_refs": refs,
        "semantic_verification_hash": _sha_obj(semantic),
        "calibration_status": "pending_explicit_authorization" if _read_json(_stage_path(root_path, action_id, "learning"), {}).get("learnable") else "blocked",
        "claim_boundary": CLAIM_BOUNDARY,
        "generated_at_utc": _utc(),
    }
    path = exp_dir / "experience_manifest.json"
    if path.exists():
        existing = _read_json(path, {})
        if _sha_obj(existing) != _sha_obj(manifest):
            raise ValueError("Immutable experience seal mismatch")
        manifest = existing
    else:
        _write_json(path, manifest)
        append_hash_chained_event(root_path / EXPERIENCE_LEDGER, {"schema": "NEXUS_EXPERIENCE_EVENT.v2.7.0", "event_type": "experience_sealed", "experience_id": exp_id, "action_id": action_id, "manifest_hash": _sha_obj(manifest), "producer_version": VERSION}, producer="experience-seal")
    _write_json(root_path / LATEST_COMPLETED_POINTER, {"schema": "NEXUS_LATEST_COMPLETED_ACTION_POINTER.v2.7.0", "action_id": action_id, "experience_id": exp_id, "updated_at_utc": _utc()})
    _write_json(root_path / LATEST_EXPERIENCE_POINTER, {"schema": "NEXUS_LATEST_VERIFIED_EXPERIENCE_POINTER.v2.7.0", "experience_id": exp_id, "action_id": action_id, "updated_at_utc": _utc()})
    _write_json(root_path / "reports" / "nexus_experience_seal_latest.json", manifest)
    try:
        _transition(root_path, action_id, "EXPERIENCE_SEALED", "verified experience sealed")
    except ValueError:
        pass
    return manifest


def calibration_status(root: str | Path, experience_id: str | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if not experience_id:
        experience_id = _read_json(root_path / LATEST_EXPERIENCE_POINTER, {}).get("experience_id")
    manifest = _read_json(root_path / "state" / "experiences" / str(experience_id) / "experience_manifest.json", {}) if experience_id else {}
    status = "blocked"
    blockers: list[str] = []
    if not manifest:
        blockers.append("missing_verified_experience")
    elif manifest.get("calibration_status") != "pending_explicit_authorization":
        blockers.append("experience_not_calibration_eligible")
    else:
        status = "pending_authorization"
    packet = {"schema": "NEXUS_CALIBRATION_STATUS.v2.7.0", "status": status, "experience_id": experience_id, "blocking_reasons": blockers, "automatic_calibration": False, "claim_boundary": CLAIM_BOUNDARY}
    _write_json(root_path / "reports" / "nexus_calibration_status_latest.json", packet)
    return packet


def calibration_authorize(root: str | Path, experience_id: str, note: str = "", expires_minutes: int = 30) -> dict[str, Any]:
    root_path = Path(root).resolve()
    manifest = _read_json(root_path / "state" / "experiences" / experience_id / "experience_manifest.json", {})
    if not manifest:
        raise ValueError("Missing verified experience")
    auth = {
        "schema": "NEXUS_CALIBRATION_AUTHORIZATION.v2.7.0",
        "experience_id": experience_id,
        "authorized_at_utc": _utc(),
        "expires_at_utc": (datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).isoformat(),
        "experience_manifest_hash": _sha_obj(manifest),
        "human_authorization": {"method": "explicit_cli", "actor": "local_human_operator", "note": note},
        "authority_boundary": {"single_experience_only": True, "automatic_calibration": False},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    auth["authorization_hash"] = _sha_obj(auth)
    _write_json(root_path / "state" / "experiences" / experience_id / "calibration_authorization.json", auth)
    return auth


def calibration_apply(root: str | Path, experience_id: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    auth = _read_json(root_path / "state" / "experiences" / experience_id / "calibration_authorization.json", {})
    manifest = _read_json(root_path / "state" / "experiences" / experience_id / "experience_manifest.json", {})
    if not auth:
        raise ValueError("Missing explicit calibration authorization")
    if _parse_utc(auth["expires_at_utc"]) < datetime.now(timezone.utc):
        raise ValueError("Calibration authorization expired")
    if auth.get("experience_manifest_hash") != _sha_obj(manifest):
        raise ValueError("Calibration authorization does not match experience")
    applied_path = root_path / "state" / "experiences" / experience_id / "calibration_applied.json"
    if applied_path.exists():
        return _read_json(applied_path, {})
    before = _read_json(root_path / CALIBRATION_STATE, {"schema": "NEXUS_ROUTE_MODELS.v2.7.0", "routes": {}})
    after = dict(before)
    event = {
        "schema": "NEXUS_CALIBRATION_APPLICATION.v2.7.0",
        "experience_id": experience_id,
        "status": "held",
        "applied": False,
        "reason": "v2.7.0 records explicit authorization but does not auto-promote routing from a single experience.",
        "route_model_before_hash": _sha_obj(before),
        "route_model_after_hash": _sha_obj(after),
        "maximum_single_update": 0.05,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(applied_path, event)
    append_hash_chained_event(root_path / CALIBRATION_LEDGER, {"schema": "NEXUS_CALIBRATION_EVENT.v2.7.0", "event_type": "calibration_held", "experience_id": experience_id, "applied": False, "producer_version": VERSION}, producer="calibration")
    return event


def calibration_replay_verify(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    chain = verify_hash_chain(root_path / CALIBRATION_LEDGER)
    packet = {"schema": "NEXUS_CALIBRATION_REPLAY_VERIFY.v2.7.0", "status": "pass" if chain.get("chain_valid") else "fail", "chain": chain, "claim_boundary": CLAIM_BOUNDARY, "generated_at_utc": _utc()}
    _write_json(root_path / "reports" / "nexus_calibration_replay_verify_latest.json", packet)
    return packet


def adaptive_coherence(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    readiness = first_learning_readiness(root_path)
    exp_chain = experience_chain_verify(root_path)
    calibration = calibration_replay_verify(root_path)
    verified_experiences = exp_chain["chain"]["chain_length"]
    dimensions = {
        "identity_integrity": 1.0 if readiness.get("epoch_chains_valid") else 0.0,
        "causal_integrity": 1.0 if readiness.get("action_chains_valid") and readiness.get("semantic_action_chain_valid") else 0.0,
        "experience_integrity": 1.0 if exp_chain.get("status") == "pass" else 0.0,
        "calibration_integrity": 1.0 if calibration.get("status") == "pass" else 0.0,
        "sample_sufficiency": min(1.0, verified_experiences / 3.0),
    }
    product = 1.0
    for value in dimensions.values():
        product *= max(0.0, min(1.0, float(value)))
    score = round(product ** (1 / len(dimensions)), 4) if dimensions else 0.0
    packet = {"schema": "NEXUS_ADAPTIVE_COHERENCE.v2.7.0", "status": "warn" if verified_experiences < 3 else "pass", "adaptive_coherence": score, "dimensions": dimensions, "verified_experience_count": verified_experiences, "sample_sufficiency": "insufficient" if verified_experiences < 3 else "forming", "claim_boundary": CLAIM_BOUNDARY, "generated_at_utc": _utc()}
    _write_json(root_path / "reports" / "nexus_adaptive_coherence_latest.json", packet)
    return packet


def emergence_report(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    coherence = adaptive_coherence(root_path)
    exp_chain = experience_chain_verify(root_path)
    packet = {
        "schema": "NEXUS_EMERGENCE_OBSERVATION.v2.7.0",
        "status": "insufficient_evidence" if exp_chain["chain"]["chain_length"] < 3 else "forming",
        "verified_experiences": exp_chain["chain"]["chain_length"],
        "calibrated_experiences": verify_hash_chain(root_path / CALIBRATION_LEDGER)["chain_length"],
        "adaptive_coherence": coherence.get("adaptive_coherence"),
        "self_organization_signals": [],
        "counter_signals": ["sample_sufficiency_insufficient"] if exp_chain["chain"]["chain_length"] < 3 else [],
        "sample_sufficiency": coherence.get("sample_sufficiency"),
        "claim_boundary": "Engineering emergence observations only. No consciousness, AGI, autonomous authority, or production safety is claimed.",
        "generated_at_utc": _utc(),
    }
    _write_json(root_path / "reports" / "nexus_emergence_observation_latest.json", packet)
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
    parser.add_argument("command", choices=[
        "recommend", "status", "authorize", "deny", "execute", "effects", "action-final-evolve",
        "validate", "finalize", "chain-verify", "semantic-verify", "receipts",
        "first-learning-readiness", "experience-readiness", "experience-seal", "experience-chain-verify",
        "calibration-status", "calibration-authorize", "calibration-apply", "calibration-replay-verify",
        "adaptive-coherence", "emergence-report"
    ])
    parser.add_argument("--root", default=".")
    parser.add_argument("--action-id", default="")
    parser.add_argument("--experience-id", default="")
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
        elif args.command == "action-final-evolve":
            packet = action_final_evolve(args.root, args.action_id)
        elif args.command == "validate":
            packet = validate(args.root, args.action_id)
        elif args.command == "finalize":
            packet = finalize(args.root, args.action_id)
        elif args.command == "chain-verify":
            packet = chain_verify(args.root)
        elif args.command == "semantic-verify":
            packet = semantic_verify(args.root, args.action_id or None)
        elif args.command == "first-learning-readiness":
            packet = first_learning_readiness(args.root)
        elif args.command == "experience-readiness":
            packet = first_learning_readiness(args.root)
        elif args.command == "experience-seal":
            packet = experience_seal(args.root, args.action_id)
        elif args.command == "experience-chain-verify":
            packet = experience_chain_verify(args.root)
        elif args.command == "calibration-status":
            packet = calibration_status(args.root, args.experience_id or None)
        elif args.command == "calibration-authorize":
            packet = calibration_authorize(args.root, args.experience_id, note=args.note, expires_minutes=args.expires_minutes)
        elif args.command == "calibration-apply":
            packet = calibration_apply(args.root, args.experience_id)
        elif args.command == "calibration-replay-verify":
            packet = calibration_replay_verify(args.root)
        elif args.command == "adaptive-coherence":
            packet = adaptive_coherence(args.root)
        elif args.command == "emergence-report":
            packet = emergence_report(args.root)
        else:
            packet = status(args.root, args.action_id or None)
    except Exception as exc:
        packet = {"schema": "NEXUS_ACTION_ERROR.v2.7.0", "status": "fail", "error": str(exc), "claim_boundary": CLAIM_BOUNDARY}
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS causal action: {packet.get('status', packet.get('authorization_status', 'ok'))} {packet.get('action_id', '')}")
    return 0 if packet.get("status", "pass") in {"pass", "warn", "blocked", "ready", "sealed", "pending_authorization", "held", "insufficient_evidence", "PROPOSED", "AUTHORIZED", "EXECUTED", "VALIDATED", "none"} or "receipt_hash" in packet else 1


if __name__ == "__main__":
    raise SystemExit(main())
