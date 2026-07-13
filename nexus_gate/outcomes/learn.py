from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.6.3"
SCHEMA = "NEXUS_RECOMMENDATION_OUTCOME_LEARNER.v2.6.3"
REPORT_LATEST = Path("reports") / "nexus_recommendation_outcome_latest.json"
CALIBRATION_LATEST = Path("state") / "coherence" / "arbiter_calibration_latest.json"
PRESSURE_MEMORY_LATEST = Path("state") / "coherence" / "pressure_memory_latest.json"
LEDGER_PATH = Path("ledger") / "recommendation_outcomes.jsonl"

CLAIM_BOUNDARY = (
    "Recommendation outcome learning is local development evidence only. It can "
    "record route outcomes, estimate route fitness, and calibrate recommendation "
    "weights. It does not prove correctness, safety, security, production readiness, "
    "model understanding, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "execute_recommendation",
    "skip_final_evolve",
    "promote_outcome_to_truth",
    "git_write",
    "arbitrary_shell_commands",
    "external_api_writes",
    "secret_access",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _append_jsonl_once(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {item.get("event_id") for item in _read_jsonl(path)}
    if row.get("event_id") in existing:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _hash_payload(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _latest_human_surface(root: Path) -> dict[str, Any]:
    base = root / "reports" / "human_surface"
    if not base.exists():
        return {"status": "missing", "path": None, "logs": []}
    dirs = sorted([path for path in base.iterdir() if path.is_dir()], key=lambda p: p.name)
    if not dirs:
        return {"status": "missing", "path": None, "logs": []}
    latest = dirs[-1]
    logs = sorted(latest.glob("*"))
    texts = []
    for path in logs:
        if path.is_file():
            try:
                texts.append(path.read_text(encoding="utf-8-sig", errors="ignore"))
            except Exception:
                texts.append("")
    failed = any(" failed." in text.lower() or "nexus step timeout" in text.lower() for text in texts)
    passed = any("passed" in text.lower() or path.name == "17_pack_compiler.json" for path, text in zip(logs, texts))
    status = "fail" if failed else "pass" if passed else "unknown"
    return {"status": status, "path": str(latest), "logs": [path.name for path in logs]}


def _route_fitness(outcome: str, coherence: dict[str, Any]) -> float:
    score = float(((coherence.get("coherence") or {}).get("score")) or 0)
    base = {"pass": 1.0, "warn": 0.65, "skipped": 0.35, "unknown": 0.25, "fail": 0.0}.get(outcome, 0.25)
    pressure_bonus = 0.15 if score >= 85 else 0.0
    return round(min(1.0, base + pressure_bonus), 3)


def _calibrate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, dict[str, Any]] = {}
    for row in rows:
        source = row.get("selected_source") or "unknown"
        bucket = by_source.setdefault(source, {"runs": 0, "pass": 0, "warn": 0, "fail": 0, "skipped": 0, "fitness_total": 0.0})
        bucket["runs"] += 1
        outcome = row.get("outcome", "unknown")
        if outcome in bucket:
            bucket[outcome] += 1
        bucket["fitness_total"] += float(row.get("route_fitness") or 0.0)
    for source, bucket in by_source.items():
        runs = max(1, int(bucket["runs"]))
        bucket["fitness_mean"] = round(float(bucket["fitness_total"]) / runs, 3)
        bucket["reliability"] = round((float(bucket["pass"]) + 0.5 * float(bucket["warn"])) / runs, 3)
        bucket["weight_adjustment"] = round((bucket["reliability"] - 0.5) * 12, 3)
        del bucket["fitness_total"]
    return {
        "schema": "NEXUS_ARBITER_CALIBRATION.v2.2.0",
        "version": VERSION,
        "generated_at_utc": _utc(),
        "source_calibration": by_source,
        "boundary": "Calibration may adjust recommendation pressure. It may not authorize execution.",
    }


def _pressure_memory(rows: list[dict[str, Any]], latest_coherence: dict[str, Any]) -> dict[str, Any]:
    scores = [float(row.get("coherence_score")) for row in rows if row.get("coherence_score") is not None]
    latest = float(((latest_coherence.get("coherence") or {}).get("score")) or 0)
    if latest:
        scores.append(latest)
    trend = "stable"
    if len(scores) >= 3:
        if scores[-1] > scores[-3] + 3:
            trend = "rising"
        elif scores[-1] < scores[-3] - 3:
            trend = "falling"
    return {
        "schema": "NEXUS_PRESSURE_MEMORY.v2.2.0",
        "version": VERSION,
        "generated_at_utc": _utc(),
        "samples": len(scores),
        "latest_coherence_score": latest,
        "trend": trend,
        "hysteresis_rule": "Do not switch route class from pressure alone until the trend persists across at least three samples.",
        "boundary": "Pressure memory is a routing signal, not authority.",
    }


def build_outcome_report(root: str | Path, intent: str = "", record: bool = True) -> dict[str, Any]:
    root_path = Path(root).resolve()
    latest_action = _read_json(root_path / "state" / "latest_action_pointer.json", {})
    action_id = latest_action.get("action_id")
    learning_receipt = _read_json(root_path / "state" / "actions" / str(action_id) / "learning.json", {}) if action_id else {}
    decision = _read_json(root_path / "reports" / "nexus_decision_envelope_latest.json", {})
    coherence = _read_json(root_path / "reports" / "nexus_coherence_field_latest.json", {})
    latest_gate = _latest_human_surface(root_path)
    selected = decision.get("selected_action") or {}
    outcome = "skipped"
    learning_status = "blocked"
    blocked_reason = "no validated causal action receipt"
    if learning_receipt.get("learnable") is True:
        outcome = (learning_receipt.get("outcome") or {}).get("classification", "unknown")
        learning_status = "learnable"
        blocked_reason = ""
    elif learning_receipt:
        learning_status = "blocked"
        blockers = learning_receipt.get("blocking_reasons") or []
        blocked_reason = ", ".join(blockers) if blockers else "learning receipt is not learnable"
    event_basis = {
        "selected": selected,
        "human_surface": latest_gate.get("path"),
        "origin_hash": ((coherence.get("origin") or {}).get("origin_manifest_hash")),
    }
    row = {
        "event_id": _hash_payload(event_basis)[:24],
        "timestamp": _utc(),
        "selected_source": selected.get("source", "unknown"),
        "selected_action": selected.get("next_loop"),
        "selected_command": selected.get("command"),
        "arbiter_score": selected.get("arbiter_score"),
        "outcome": outcome,
        "human_surface_path": latest_gate.get("path"),
        "action_id": action_id,
        "learning_receipt_hash": learning_receipt.get("receipt_hash"),
        "learning_status": learning_status,
        "blocked_reason": blocked_reason,
        "law": "No receipt, no learning.",
        "coherence_score": ((coherence.get("coherence") or {}).get("score")),
        "lineage_entropy": ((coherence.get("coherence") or {}).get("lineage_entropy")),
        "route_fitness": _route_fitness(outcome, coherence),
        "followup_needed": outcome not in {"pass", "warn"},
        "lesson": (
            "Validated causal action receipt recorded; future recommendations may adjust source pressure from calibration."
            if learning_status == "learnable"
            else "No validated causal receipt exists; outcome remains observational and cannot calibrate route pressure."
        ),
    }
    if record and learning_status == "learnable":
        _append_jsonl_once(root_path / LEDGER_PATH, row)
    rows = _read_jsonl(root_path / LEDGER_PATH)
    if row.get("event_id") not in {item.get("event_id") for item in rows}:
        rows.append(row)
    calibration = _calibrate(rows)
    pressure = _pressure_memory(rows, coherence)
    report = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "phase": "Outcome-Aware Arbiter",
        "status": "pass" if learning_status == "learnable" else "warn",
        "learning_status": learning_status,
        "blocked_reason": blocked_reason,
        "law": "No receipt, no learning.",
        "generated_at_utc": _utc(),
        "intent": intent,
        "latest_outcome": row,
        "calibration": calibration,
        "pressure_memory": pressure,
        "read_surfaces": [
            "reports/nexus_decision_envelope_latest.json",
            "reports/nexus_coherence_field_latest.json",
            "reports/human_surface/*",
            "state/actions/<action_id>/learning.json",
        ],
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            CALIBRATION_LATEST.as_posix(),
            PRESSURE_MEMORY_LATEST.as_posix(),
            LEDGER_PATH.as_posix(),
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return report


def write_outcome_report(root: str | Path, intent: str = "", record: bool = True) -> dict[str, Any]:
    root_path = Path(root).resolve()
    report = build_outcome_report(root_path, intent=intent, record=record)
    _write_json(root_path / REPORT_LATEST, report)
    _write_json(root_path / CALIBRATION_LATEST, report["calibration"])
    _write_json(root_path / PRESSURE_MEMORY_LATEST, report["pressure_memory"])
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS recommendation outcome learning.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Compile recommendation outcome learning.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-record", action="store_true")
    args = parser.parse_args(argv)
    packet = write_outcome_report(args.root, intent=args.intent, record=not args.no_record)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        latest = packet["latest_outcome"]
        print(f"NEXUS outcome learner: {packet['status']} fitness={latest.get('route_fitness')}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
