from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.7.1"
SCHEMA = "NEXUS_BREATH_PULSE.v2.7.1"
REPORT_LATEST = Path("reports") / "nexus_breath_pulse_latest.json"
STATE_LATEST = Path("state") / "breath" / "nexus_breath_pulse_latest.json"

SURFACES = {
    "origin": Path("reports/nexus_origin_seal_latest.json"),
    "epoch": Path("reports/nexus_epoch_integrity_seal_latest.json"),
    "coherence": Path("reports/nexus_coherence_field_latest.json"),
    "decision": Path("reports/nexus_decision_envelope_latest.json"),
    "experience_readiness": Path("reports/nexus_experience_readiness_latest.json"),
    "emergence": Path("reports/nexus_emergence_observation_latest.json"),
    "runtime_hygiene": Path("reports/nexus_runtime_hygiene_latest.json"),
    "feedback_interface": Path("reports/nexus_feedback_interface_report_latest.json"),
    "latest_epoch_pointer": Path("state/latest_epoch_pointer.json"),
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


def _freshness(root: Path, now: datetime) -> dict[str, Any]:
    entries = []
    for name, rel in SURFACES.items():
        path = root / rel
        packet = _read_json(path)
        age = _age_seconds(path, now)
        status = _surface_status(packet) if packet else ("missing" if age is None else "unknown")
        stale = age is None or age > 60 * 60 * 24
        entries.append({
            "surface": name,
            "path": str(rel).replace("\\", "/"),
            "status": status,
            "age_seconds": age,
            "fresh": not stale,
        })
    return {
        "surfaces": entries,
        "missing": [item["surface"] for item in entries if item["status"] == "missing"],
        "stale": [item["surface"] for item in entries if not item["fresh"]],
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
    if fail_count:
        level = "critical"
    elif score < 70:
        level = "high"
    elif score < 88:
        level = "medium"
    else:
        level = "low"
    return {
        "score": score,
        "level": level,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "stale_count": stale_count,
    }


def _rhythm(pressure: dict[str, Any], git_scope: dict[str, Any], freshness: dict[str, Any]) -> dict[str, Any]:
    source_pressure = git_scope.get("source_pressure")
    level = pressure["level"]
    if level == "critical":
        phase = "hold"
        command = ".\\scripts\\nexus.ps1 status"
        why = "Critical pressure detected; observe before mutation."
    elif source_pressure == "canonical_change":
        phase = "exhale"
        command = ".\\scripts\\nexus.ps1 predictive-evolve"
        why = "Canonical source changed; plan targeted gates before full evolve."
    elif freshness["stale"]:
        phase = "inhale"
        command = ".\\scripts\\nexus.ps1 breath"
        why = "Evidence is stale or missing; refresh orientation before routing."
    elif level in {"medium", "high"}:
        phase = "hold"
        command = ".\\scripts\\nexus.ps1 runtime-hygiene"
        why = "Pressure is elevated; classify runtime churn before compounding."
    else:
        phase = "inhale"
        command = ".\\scripts\\nexus.ps1 experience-readiness"
        why = "Field is stable enough to inspect verified-experience readiness."
    return {
        "phase": phase,
        "cadence": {
            "inhale": "read identity/evidence",
            "hold": "stabilize pressure",
            "exhale": "run bounded recommendation gate",
        },
        "recommended_next_command": command,
        "why": why,
    }


def build_breath_packet(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    now = _utc_now()
    freshness = _freshness(root_path, now)
    git = _git_scope(root_path)
    statuses = [item["status"] for item in freshness["surfaces"]]
    pressure = _pressure(statuses, git["dirty_count"], len(freshness["stale"]))
    rhythm = _rhythm(pressure, git, freshness)
    status = "pass" if pressure["level"] in {"low", "medium"} and not freshness["missing"] else "warn"
    if pressure["level"] == "critical":
        status = "fail"
    return {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": status,
        "generated_at_utc": _iso(now),
        "breath": rhythm,
        "runtime_pressure": pressure,
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
