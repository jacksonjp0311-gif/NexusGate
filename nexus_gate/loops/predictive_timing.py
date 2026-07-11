from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1.1.6"
SCHEMA = "NEXUS_PREDICTIVE_GATE_TIMING.v1.1.6"
REPORT_LATEST = Path("reports") / "nexus_predictive_gate_timing_latest.json"
STATE_LATEST = Path("state") / "loops" / "nexus_predictive_gate_timing_latest.json"
TIMING_LEDGER = Path("ledger") / "runtime_gate_timings.jsonl"

CLAIM_BOUNDARY = (
    "Predictive Gate Timing is local development evidence only. It estimates "
    "runtime pressure from prior local reports and recommends bounded command "
    "budgets; it does not prove future duration, correctness, safety, security, "
    "production readiness, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "bypass_gates",
    "hide_failures",
    "autonomous_timeout_extension",
    "arbitrary_shell_commands",
    "git_write",
    "external_api_writes",
]

STEP_ORDER = [
    "01_python_compile",
    "02_unit_tests",
    "03_nexus_compiler",
    "04_adapter_compiler",
    "05_receptor_compiler",
    "06_bridge_compiler",
    "07_runtime_compiler",
    "08_evidence_compaction",
    "09_interconnect_compiler",
    "10_feedback_compiler",
    "11_self_healing_compiler",
    "12_ai_feedback_interface",
    "13_electron_environment",
    "14_electron_preflight",
    "15_reflective_loop",
    "16_domain_intelligence",
    "16b_meta_orchestrator_gate",
    "16c_loop_orchestrator",
    "17_pack_compiler",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")
    except Exception:
        return ""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _step_id(path: Path) -> str:
    return path.stem


def _step_status(path: Path) -> str:
    text = _read_text(path)
    lower = text.lower()
    if "nexus step timeout" in lower or "timed out" in lower:
        return "timeout"
    if "traceback" in lower or '"status": "fail"' in lower or " failed" in lower:
        return "fail"
    if '"status": "warn"' in lower or "warning" in lower:
        return "warn"
    return "pass"


def _collect_runs(root: Path, max_runs: int) -> list[dict[str, Any]]:
    base = root / "reports" / "human_surface"
    if not base.exists():
        return []
    sessions = [p for p in base.iterdir() if p.is_dir()]
    sessions = sorted(sessions, key=lambda p: p.name, reverse=True)[:max_runs]
    runs: list[dict[str, Any]] = []
    for session in sessions:
        files = sorted(
            [p for p in session.iterdir() if p.is_file()],
            key=lambda p: p.stat().st_mtime,
        )
        if not files:
            continue
        previous = session.stat().st_mtime
        steps: list[dict[str, Any]] = []
        for file_path in files:
            current = file_path.stat().st_mtime
            duration = max(0.0, current - previous)
            previous = current
            steps.append(
                {
                    "step": _step_id(file_path),
                    "path": str(file_path.relative_to(root)).replace("\\", "/"),
                    "duration_seconds": round(duration, 3),
                    "status": _step_status(file_path),
                }
            )
        runs.append(
            {
                "session": session.name,
                "step_count": len(steps),
                "total_seconds": round(max(0.0, files[-1].stat().st_mtime - session.stat().st_mtime), 3),
                "steps": steps,
            }
        )
    return runs


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((len(values) - 1) * q)))
    return values[idx]


def _recommend_timeout(baseline: float, latest: float, timed_out: bool, step: str) -> int:
    minimum = 60
    if step == "17_pack_compiler":
        minimum = 420
    target = max(baseline * 1.65, latest * 1.35, minimum)
    if timed_out:
        target = max(target, latest * 2.0, minimum)
    return int(min(900, max(minimum, round(target / 30) * 30)))


def _adaptive_timeout(p90: float, step: str) -> int:
    minimum = 60
    if step == "17_pack_compiler":
        minimum = 420
    maximum = 900
    target = max(minimum, min(maximum, p90 * 1.5 if p90 > 0 else minimum))
    return int(round(target / 30) * 30)


def _pressure_level(ratio: float, timed_out: bool, failed: bool) -> str:
    if failed or timed_out or ratio >= 1.75:
        return "high"
    if ratio >= 1.25:
        return "medium"
    return "low"


def _analyze_steps(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_step: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        for step in run["steps"]:
            by_step.setdefault(step["step"], []).append(step)

    analysis: list[dict[str, Any]] = []
    for step_name in STEP_ORDER:
        samples = by_step.get(step_name, [])
        if not samples:
            continue
        durations = [float(item["duration_seconds"]) for item in samples]
        latest = durations[0]
        baseline = statistics.median(durations)
        p90 = _percentile(durations, 0.9)
        ratio = latest / baseline if baseline > 0 else 1.0
        statuses = [item["status"] for item in samples]
        timed_out = statuses[0] == "timeout" or "timeout" in statuses[:3]
        failed = statuses[0] == "fail"
        level = _pressure_level(ratio, timed_out, failed)
        analysis.append(
            {
                "step": step_name,
                "latest_seconds": round(latest, 3),
                "median_seconds": round(baseline, 3),
                "p90_seconds": round(p90, 3),
                "sample_count": len(samples),
                "latest_status": statuses[0],
                "pressure_level": level,
                "drift_ratio": round(ratio, 3),
                "recommended_timeout_seconds": _recommend_timeout(p90 or baseline, latest, timed_out, step_name),
            }
        )
    return analysis


def _repo_pressure(root: Path) -> dict[str, Any]:
    tracked = ["nexus_gate", "tests", "electron", "scripts", "docs"]
    counts: dict[str, int] = {}
    for rel in tracked:
        base = root / rel
        if not base.exists():
            counts[rel] = 0
            continue
        counts[rel] = sum(1 for p in base.rglob("*") if p.is_file())
    return {
        "tracked_file_counts": counts,
        "total_tracked_files": sum(counts.values()),
    }


def _git_scope(root: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception:
        return {"dirty_count": 0, "changed_files": [], "changed_file_count": 0, "scope": "unknown"}
    files: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        files.append(line[3:].strip().replace("\\", "/"))
    scope = _classify_scope(files)
    return {
        "dirty_count": len(files),
        "changed_file_count": len(files),
        "changed_files": files[:80],
        "scope": scope,
    }


def _classify_scope(files: list[str]) -> str:
    if not files:
        return "clean"
    docs = [p for p in files if p.startswith("docs/") or p in {"README.md", "AGENTS.md"} or p.endswith(".md")]
    electron = [p for p in files if p.startswith("electron/") or p.endswith((".js", ".css", ".html"))]
    python = [p for p in files if p.startswith("nexus_gate/") or p.startswith("tests/") or p.endswith(".py")]
    scripts = [p for p in files if p.startswith("scripts/") or p.endswith((".ps1", ".sh"))]
    if len(docs) == len(files):
        return "docs_only"
    if len(electron) == len(files):
        return "electron_only"
    if len(python) == len(files):
        return "python_only"
    if len(scripts) == len(files):
        return "scripts_only"
    return "mixed"


def _gate_selection_policy(scope: str, has_high_pressure: bool) -> dict[str, Any]:
    if has_high_pressure:
        return {
            "policy_id": "runtime-pressure-first",
            "recommended_command": ".\\scripts\\nexus.ps1 predictive-timing",
            "why": "Runtime pressure is high; inspect timing and run targeted gates before repeating full evolve.",
        }
    if scope == "docs_only":
        return {
            "policy_id": "docs-targeted-first",
            "recommended_command": 'python -m unittest discover -s tests -p "test_readme*.py"',
            "why": "Only docs/readme surfaces changed; run targeted docs/readme tests before full evolve.",
        }
    if scope == "electron_only":
        return {
            "policy_id": "electron-smoke-first",
            "recommended_command": "cd electron; npm run smoke",
            "why": "Only Electron/UI surfaces changed; run Electron smoke before full evolve.",
        }
    if scope == "python_only":
        return {
            "policy_id": "python-targeted-first",
            "recommended_command": 'python -m unittest discover -s tests -p "<targeted_test.py>"',
            "why": "Python/test surfaces changed; run targeted unit tests before full evolve.",
        }
    return {
        "policy_id": "normal-evolve-when-ready",
        "recommended_command": ".\\scripts\\nexus.ps1 evolve",
        "why": "Scope is clean or mixed; normal evolve remains the final local seal when patch scope is ready.",
    }


def _next_action(step_analysis: list[dict[str, Any]], gate_policy: dict[str, Any]) -> dict[str, str]:
    high = [item for item in step_analysis if item["pressure_level"] == "high"]
    medium = [item for item in step_analysis if item["pressure_level"] == "medium"]
    if high:
        step = high[0]["step"]
        return {
            "recommended_next_command": '.\\scripts\\nexus.ps1 predictive-timing',
            "recommended_next_loop": "predictive-gate-timing",
            "why": f"{step} shows high runtime pressure; inspect timing forecast before another full evolve.",
        }
    if medium:
        step = medium[0]["step"]
        return {
            "recommended_next_command": 'python -m unittest discover -s tests -p "<targeted_test.py>"',
            "recommended_next_loop": "targeted-gate-first",
            "why": f"{step} shows medium drift; run targeted tests before full evolve to reduce token and wall-clock waste.",
        }
    if gate_policy.get("policy_id") != "normal-evolve-when-ready":
        return {
            "recommended_next_command": gate_policy["recommended_command"],
            "recommended_next_loop": gate_policy["policy_id"],
            "why": gate_policy["why"],
        }
    return {
        "recommended_next_command": ".\\scripts\\nexus.ps1 evolve",
        "recommended_next_loop": "normal-evolve",
        "why": "No timing pressure above baseline; normal evolve is acceptable when the patch scope is ready.",
    }


def build_predictive_timing_packet(root: str | Path, max_runs: int = 12) -> dict[str, Any]:
    root_path = Path(root).resolve()
    runs = _collect_runs(root_path, max_runs=max_runs)
    analysis = _analyze_steps(runs)
    highest = sorted(
        analysis,
        key=lambda item: ({"high": 3, "medium": 2, "low": 1}.get(item["pressure_level"], 0), item["drift_ratio"]),
        reverse=True,
    )[:5]
    git_scope = _git_scope(root_path)
    has_high_pressure = any(item["pressure_level"] == "high" for item in analysis)
    gate_policy = _gate_selection_policy(git_scope["scope"], has_high_pressure)
    next_action = _next_action(analysis, gate_policy)
    status = "pass"
    if has_high_pressure:
        status = "warn"

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "predictive_gate_timing",
        "status": status,
        "generated_utc": _utc(),
        "run_sample_count": len(runs),
        "read_surfaces": ["reports/human_surface/*", "git status --porcelain"],
        "write_surfaces": [REPORT_LATEST.as_posix(), STATE_LATEST.as_posix(), TIMING_LEDGER.as_posix()],
        "runtime_pressure": highest,
        "step_analysis": analysis,
        "repo_pressure": _repo_pressure(root_path),
        "git_scope": git_scope,
        "adaptive_timeout_policy": {
            "formula": "timeout = max(min_timeout, min(max_timeout, p90 * 1.5))",
            "min_timeout_seconds": 60,
            "pack_min_timeout_seconds": 420,
            "max_timeout_seconds": 900,
            "mode": "recommendation_only",
        },
        "gate_selection_policy": gate_policy,
        "recommendation": next_action,
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "autonomous_timeout_extension": False,
            "bypass_gates": False,
            "hide_failures": False,
            "repo_mutation": False,
            "arbitrary_shell_execution": False,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_outputs(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    _write_json(root_path / REPORT_LATEST, packet)
    _write_json(
        root_path / STATE_LATEST,
        {
            "schema": packet["schema"],
            "version": packet["version"],
            "status": packet["status"],
            "generated_utc": packet["generated_utc"],
            "run_sample_count": packet["run_sample_count"],
            "runtime_pressure": packet["runtime_pressure"],
            "gate_selection_policy": packet["gate_selection_policy"],
            "recommendation": packet["recommendation"],
            "blocked_actions": packet["blocked_actions"],
            "claim_boundary": packet["claim_boundary"],
        },
    )
    timestamp = packet["generated_utc"]
    git_scope = packet.get("git_scope", {})
    rows = []
    for item in packet.get("step_analysis", []):
        rows.append(
            {
                "timestamp": timestamp,
                "gate": item["step"],
                "duration_sec": item["latest_seconds"],
                "status": item["latest_status"],
                "repo_dirty_count": git_scope.get("dirty_count", 0),
                "changed_files": git_scope.get("changed_file_count", 0),
                "pressure_level": item["pressure_level"],
                "drift_ratio": item["drift_ratio"],
                "recommended_timeout_seconds": _adaptive_timeout(item.get("p90_seconds", 0), item["step"]),
            }
        )
    _append_jsonl(root_path / TIMING_LEDGER, rows)


def render(packet: dict[str, Any]) -> str:
    pressure = packet.get("runtime_pressure") or []
    top = pressure[0] if pressure else {}
    rec = packet.get("recommendation", {})
    return "\n".join(
        [
            "NEXUS PREDICTIVE GATE TIMING",
            f"Version: v{packet.get('version')}",
            f"Status: {packet.get('status')}",
            f"Runs sampled: {packet.get('run_sample_count')}",
            f"Top pressure: {top.get('step', 'none')} {top.get('pressure_level', 'low')}",
            f"Next: {rec.get('recommended_next_command')}",
            f"Why: {rec.get('why')}",
            "Boundary: recommendation-only; timing forecasts do not authorize bypassing gates.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS predictive gate timing report.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-runs", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    packet = build_predictive_timing_packet(args.root, max_runs=args.max_runs)
    write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
