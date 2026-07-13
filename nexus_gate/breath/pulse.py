from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.8.0"
SCHEMA = "NEXUS_BREATH_PULSE.v2.8.0"
REPORT_LATEST = Path("reports") / "nexus_breath_pulse_latest.json"
STATE_LATEST = Path("state") / "breath" / "nexus_breath_pulse_latest.json"
HISTORY = Path("state") / "breath" / "nexus_breath_history.jsonl"

SURFACES = {
    "origin": Path("reports/nexus_origin_seal_latest.json"),
    "epoch": Path("reports/nexus_epoch_integrity_seal_latest.json"),
    "coherence": Path("reports/nexus_coherence_field_latest.json"),
    "decision": Path("reports/nexus_decision_envelope_latest.json"),
    "experience_readiness": Path("reports/nexus_experience_readiness_latest.json"),
    "emergence": Path("reports/nexus_emergence_observation_latest.json"),
    "runtime_hygiene": Path("reports/nexus_runtime_hygiene_latest.json"),
    "feedback_interface": Path("reports/nexus_feedback_interface_report_latest.json"),
    "telemetry_health": Path("reports/nexus_telemetry_health_latest.json"),
    "telemetry_field": Path("reports/nexus_telemetry_field_latest.json"),
    "conductance_field": Path("reports/nexus_conductance_field_latest.json"),
    "latest_epoch_pointer": Path("state/latest_epoch_pointer.json"),
}

PRODUCERS = {
    "origin": "origin-seal",
    "epoch": "epoch-seal",
    "coherence": "coherence-field",
    "decision": "decision-envelope",
    "experience_readiness": "experience-readiness",
    "emergence": "emergence-report",
    "runtime_hygiene": "runtime-hygiene",
    "feedback_interface": "interface",
    "telemetry_health": "telemetry-health",
    "telemetry_field": "telemetry-fuse",
    "conductance_field": "conductance-field",
    "latest_epoch_pointer": "epoch-seal",
}

COMMANDS = {
    "status": {"powershell": ".\\scripts\\nexus.ps1 status", "bash": "./scripts/nexus.sh status", "python": "python -m nexus_gate.compiler --root . --json"},
    "predictive-evolve": {"powershell": ".\\scripts\\nexus.ps1 predictive-evolve", "bash": "./scripts/nexus.sh predictive-evolve", "python": "python -m nexus_gate.loops.predictive_evolve --root . --json"},
    "runtime-hygiene": {"powershell": ".\\scripts\\nexus.ps1 runtime-hygiene", "bash": "./scripts/nexus.sh runtime-hygiene", "python": "python -m nexus_gate.hygiene.runtime_churn --root . --json"},
    "experience-readiness": {"powershell": ".\\scripts\\nexus.ps1 experience-readiness", "bash": "./scripts/nexus.sh experience-readiness", "python": "python -m nexus_gate.actions.cli experience-readiness --root . --json"},
    "action-status": {"powershell": ".\\scripts\\nexus.ps1 action-status", "bash": "./scripts/nexus.sh action-status", "python": "python -m nexus_gate.actions.cli status --root . --json"},
    "action-effects": {"powershell": ".\\scripts\\nexus.ps1 action-effects", "bash": "./scripts/nexus.sh action-effects", "python": "python -m nexus_gate.actions.cli effects --root . --json"},
    "action-final-evolve": {"powershell": ".\\scripts\\nexus.ps1 action-final-evolve", "bash": "./scripts/nexus.sh action-final-evolve", "python": "python -m nexus_gate.actions.cli action-final-evolve --root . --json"},
    "action-validate": {"powershell": ".\\scripts\\nexus.ps1 action-validate", "bash": "./scripts/nexus.sh action-validate", "python": "python -m nexus_gate.actions.cli validate --root . --json"},
    "calibration-status": {"powershell": ".\\scripts\\nexus.ps1 calibration-status", "bash": "./scripts/nexus.sh calibration-status", "python": "python -m nexus_gate.actions.cli calibration-status --root . --json"},
    "telemetry-health": {"powershell": ".\\scripts\\nexus.ps1 telemetry-health", "bash": "./scripts/nexus.sh telemetry-health", "python": "python -m nexus_gate.telemetry.cli health --root . --json"},
    "telemetry-fuse": {"powershell": ".\\scripts\\nexus.ps1 telemetry-fuse", "bash": "./scripts/nexus.sh telemetry-fuse", "python": "python -m nexus_gate.telemetry.cli fuse --root . --json"},
    "conductance-field": {"powershell": ".\\scripts\\nexus.ps1 conductance-field", "bash": "./scripts/nexus.sh conductance-field", "python": "python -m nexus_gate.field.cli field --root . --json"},
}

BLOCKED_ACTIONS = [
    "execute_without_authorization",
    "calibrate_without_verified_experience",
    "treat_breath_as_evolve_pass",
    "self_authorize_mutation",
    "hide_runtime_pressure",
]

CLAIM_BOUNDARY = (
    "NEXUS Breath is a local read-only vital-sign packet. It summarizes freshness, "
    "pressure, and readiness. It does not execute commands, authorize actions, "
    "prove correctness, replace evolve, or grant autonomous authority."
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def _git_scope(root: Path) -> dict[str, Any]:
    status = _run_git(root, ["status", "--short"])
    rows = [line for line in status.stdout.splitlines() if line.strip()]
    changed = []
    for row in rows:
      path = row[3:].strip() if len(row) > 3 else row.strip()
      changed.append(path.replace("\\", "/"))
    return {
        "status_available": status.returncode == 0,
        "dirty_count": len(rows),
        "changed_paths_sample": changed[:12],
        "source_pressure": _source_pressure(changed),
    }


def _source_pressure(paths: list[str]) -> str:
    canonical_prefixes = (
        "nexus_gate/",
        "scripts/",
        "tests/",
        "docs/",
        "registry/",
        "schemas/",
        "electron/renderer/",
        "README.md",
        "AGENTS.md",
    )
    if any(path.startswith(canonical_prefixes) or path in canonical_prefixes for path in paths):
        return "canonical_change"
    if paths:
        return "runtime_or_generated_change"
    return "clear"


def _packet_hash(packet: Any) -> str:
    return hashlib.sha256(json.dumps(packet, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _age_seconds(path: Path, now: datetime) -> int | None:
    if not path.exists():
        return None
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return max(0, int((now - modified).total_seconds()))


def _surface_status(packet: dict[str, Any]) -> str:
    raw = str(packet.get("status") or packet.get("overall_status") or packet.get("state") or "unknown").lower()
    if raw in {"pass", "ready", "ok", "clean", "stable", "coherent"}:
        return "pass"
    if raw in {"warn", "warning", "blocked", "insufficient_evidence", "forming"}:
        return "warn"
    if raw in {"fail", "failed", "invalid", "error"}:
        return "fail"
    return raw or "unknown"


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _semantic_age(packet: dict[str, Any], path: Path, now: datetime) -> tuple[int | None, str]:
    timestamp = packet.get("generated_at_utc") or packet.get("retrieved_at_utc") or packet.get("observed_at_utc")
    parsed = _parse_time(timestamp)
    if parsed:
        return max(0, int((now - parsed).total_seconds())), "packet_timestamp"
    return _age_seconds(path, now), "filesystem_mtime_fallback"


def _classify_freshness(packet: dict[str, Any], path: Path, now: datetime) -> dict[str, Any]:
    if not path.exists():
        return {"semantic_freshness": "missing", "age_seconds": None, "fresh": False, "freshness_source": "missing"}
    age, source = _semantic_age(packet, path, now)
    if not packet:
        semantic = "unverifiable"
    elif packet.get("source_epoch_id") and packet.get("source_epoch_id") != _read_json(path.parent.parent / "latest_epoch_pointer.json").get("source_epoch_id"):
        semantic = "identity_mismatch"
    elif age is None:
        semantic = "unverifiable"
    elif age > 60 * 60 * 24:
        semantic = "stale"
    elif age > 60 * 60 * 6:
        semantic = "aging"
    else:
        semantic = "fresh"
    return {
        "semantic_freshness": semantic,
        "age_seconds": age,
        "fresh": semantic == "fresh",
        "freshness_source": source,
    }


def _freshness(root: Path, now: datetime) -> dict[str, Any]:
    entries = []
    for name, rel in SURFACES.items():
        path = root / rel
        packet = _read_json(path)
        semantic = _classify_freshness(packet, path, now)
        status = _surface_status(packet) if packet else ("missing" if not path.exists() else "unknown")
        entries.append({
            "surface": name,
            "path": str(rel).replace("\\", "/"),
            "producer_command_id": PRODUCERS.get(name),
            "status": status,
            "packet_hash": _packet_hash(packet) if packet else None,
            **semantic,
        })
    return {
        "surfaces": entries,
        "missing": [item["surface"] for item in entries if item["status"] == "missing"],
        "stale": [item["surface"] for item in entries if item["semantic_freshness"] in {"stale", "identity_mismatch", "unverifiable", "missing"}],
        "aging": [item["surface"] for item in entries if item["semantic_freshness"] == "aging"],
    }


def _pressure(statuses: list[str], dirty_count: int, stale_count: int) -> dict[str, Any]:
    fail_count = statuses.count("fail")
    warn_count = statuses.count("warn")
    score = 100
    score -= min(40, fail_count * 18)
    score -= min(28, warn_count * 6)
    score -= min(16, stale_count * 4)
    score -= min(16, dirty_count * 2)
    score = max(0, score)
    vitality = score
    pressure_score = 100 - vitality
    if fail_count:
        level = "critical"
    elif pressure_score > 35:
        level = "high"
    elif pressure_score > 15:
        level = "medium"
    else:
        level = "low"
    return {
        "vitality_score": vitality,
        "pressure_score": pressure_score,
        "score": vitality,
        "level": level,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "stale_count": stale_count,
    }


def _latest_action(root: Path) -> dict[str, Any]:
    pointer = _read_json(root / "state" / "latest_action_pointer.json")
    action_id = pointer.get("action_id") or pointer.get("latest_action_id")
    if not action_id:
        return {"active": False}
    lifecycle = _read_json(root / "state" / "actions" / action_id / "lifecycle.json")
    status = str(lifecycle.get("state") or lifecycle.get("status") or pointer.get("state") or "unknown").upper()
    return {"active": status not in {"LEARNABLE", "NOT_LEARNABLE", "CALIBRATED", "DENIED", "EXPIRED", "STALE", "INVALID", "FAILED", ""}, "action_id": action_id, "state": status}


def _lifecycle_recommendation(lifecycle: dict[str, Any]) -> tuple[str | None, str | None]:
    state = lifecycle.get("state", "")
    if not lifecycle.get("active"):
        return None, None
    if state == "AUTHORIZED":
        return "action-status", "Authorized action is pending; inspect before execution."
    if state == "EXECUTED":
        return "action-effects", "Executed action is missing effect proof."
    if state == "EFFECTS_CAPTURED":
        return "action-final-evolve", "Effects exist but action-bound final verification is pending."
    if state in {"VALIDATION_RECORDED", "VALIDATED_PASS"}:
        return "action-validate", "Validation state is incomplete; inspect before plasticity."
    if state in {"LEARNABLE", "CALIBRATION_PENDING"}:
        return "calibration-status", "Verified experience awaits calibration decision."
    return "action-status", "Active lifecycle exists; route attention there before broad work."


def _history_stats(root: Path, pressure_score: int, phase: str, now: datetime) -> dict[str, Any]:
    hist = root / HISTORY
    rows = []
    if hist.exists():
        for line in hist.read_text(encoding="utf-8").splitlines()[-20:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    if len(rows) < 2:
        trend = "insufficient_history"
        delta = 0
        baseline = pressure_score
    else:
        prior = [float(row.get("pressure_score", 0)) for row in rows[-8:]]
        baseline = sum(prior) / len(prior)
        delta = pressure_score - prior[-1]
        if pressure_score > baseline + 15:
            trend = "critical"
        elif delta > 4:
            trend = "rising"
        elif delta < -4:
            trend = "recovering"
        else:
            trend = "stable"
    last_phase = rows[-1].get("phase") if rows else None
    return {
        "history_count": len(rows),
        "pressure_delta": round(delta, 3),
        "pressure_trend": trend,
        "baseline_pressure": round(baseline, 3),
        "previous_phase": last_phase,
        "phase_hysteresis": "hard_transition" if not last_phase or last_phase == phase or trend == "critical" else "pending_second_pulse",
    }


def _rhythm(pressure: dict[str, Any], git_scope: dict[str, Any], freshness: dict[str, Any], lifecycle: dict[str, Any]) -> dict[str, Any]:
    source_pressure = git_scope.get("source_pressure")
    level = pressure["level"]
    lifecycle_command, lifecycle_why = _lifecycle_recommendation(lifecycle)
    if lifecycle_command:
        phase = "hold"
        command_id = lifecycle_command
        why = lifecycle_why
    elif level == "critical":
        phase = "hold"
        command_id = "status"
        why = "Critical pressure detected; observe before mutation."
    elif source_pressure == "canonical_change":
        phase = "exhale"
        command_id = "predictive-evolve"
        why = "Canonical source changed; plan targeted gates before full evolve."
    elif freshness["stale"]:
        phase = "inhale"
        stale = freshness["stale"][0]
        command_id = PRODUCERS.get(stale, "status")
        why = f"{stale} evidence is stale or missing; refresh its producer, not Breath itself."
    elif level in {"medium", "high"}:
        phase = "hold"
        command_id = "runtime-hygiene"
        why = "Pressure is elevated; classify runtime churn before compounding."
    else:
        phase = "inhale"
        command_id = "experience-readiness"
        why = "Field is stable enough to inspect verified-experience readiness."
    return {
        "phase": phase,
        "cadence": {
            "inhale": "read identity/evidence",
            "hold": "stabilize pressure",
            "exhale": "run bounded recommendation gate",
        },
        "recommended_command_id": command_id,
        "recommended_command_arguments": {},
        "recommended_next_command": COMMANDS.get(command_id, {}).get("powershell", command_id),
        "command_renderings": COMMANDS.get(command_id, {}),
        "why": why,
    }


def build_breath_packet(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    now = _utc_now()
    freshness = _freshness(root_path, now)
    git = _git_scope(root_path)
    lifecycle = _latest_action(root_path)
    statuses = [item["status"] for item in freshness["surfaces"]]
    pressure = _pressure(statuses, git["dirty_count"], len(freshness["stale"]))
    rhythm = _rhythm(pressure, git, freshness, lifecycle)
    history = _history_stats(root_path, pressure["pressure_score"], rhythm["phase"], now)
    status = "pass" if pressure["level"] in {"low", "medium"} and not freshness["missing"] else "warn"
    if pressure["level"] == "critical":
        status = "fail"
    return {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": status,
        "generated_at_utc": _iso(now),
        "pulse_id": _packet_hash({"at": _iso(now), "git": git, "freshness": freshness}),
        "breath": rhythm,
        "vitality": {"score": pressure["vitality_score"], "level": "stable" if pressure["vitality_score"] >= 85 else "strained"},
        "pressure": {"score": pressure["pressure_score"], "level": pressure["level"]},
        "runtime_pressure": pressure,
        "pressure_trend": history,
        "active_lifecycle": lifecycle,
        "semantic_freshness": {item["surface"]: item["semantic_freshness"] for item in freshness["surfaces"]},
        "telemetry_health": {
            "health": next((item for item in freshness["surfaces"] if item["surface"] == "telemetry_health"), {}),
            "field": next((item for item in freshness["surfaces"] if item["surface"] == "telemetry_field"), {}),
        },
        "conductance_field_health": next((item for item in freshness["surfaces"] if item["surface"] == "conductance_field"), {}),
        "freshness": freshness,
        "git_scope": git,
        "read_surfaces": [str(path).replace("\\", "/") for path in SURFACES.values()],
        "write_surfaces": [
            str(REPORT_LATEST).replace("\\", "/"),
            str(STATE_LATEST).replace("\\", "/"),
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_breath_packet(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    packet = build_breath_packet(root_path)
    _write_json(root_path / REPORT_LATEST, packet)
    _write_json(root_path / STATE_LATEST, packet)
    hist = root_path / HISTORY
    hist.parent.mkdir(parents=True, exist_ok=True)
    hist_row = {
        "pulse_id": packet["pulse_id"],
        "generated_at_utc": packet["generated_at_utc"],
        "vitality_score": packet["vitality"]["score"],
        "pressure_score": packet["pressure"]["score"],
        "phase": packet["breath"]["phase"],
        "dirty_count": packet["git_scope"]["dirty_count"],
        "canonical_change_count": 1 if packet["git_scope"]["source_pressure"] == "canonical_change" else 0,
        "runtime_change_count": 1 if packet["git_scope"]["source_pressure"] == "runtime_or_generated_change" else 0,
        "stale_surface_count": len(packet["freshness"]["stale"]),
        "failed_surface_count": packet["runtime_pressure"]["fail_count"],
        "active_action_state": packet["active_lifecycle"].get("state"),
        "telemetry_freshness": packet["semantic_freshness"].get("telemetry_field"),
    }
    with hist.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(hist_row, sort_keys=True) + "\n")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS breath pulse.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_breath_packet(args.root)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        breath = packet["breath"]
        print(f"NEXUS breath: {breath['phase']} -> {breath['recommended_next_command']}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
