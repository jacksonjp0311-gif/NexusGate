"""NEXUS GATE self-healing feedback engine.

This module imports the CMS pattern into NEXUS:

feedback finding -> typed repair recommendation -> dry-run plan -> apply gate

The engine is deliberately conservative. It reports and plans repairs. It does
not write target files, commit, push, call APIs, or promote memory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any, Dict, List


CLAIM_BOUNDARY = (
    "Self-healing report is local development evidence only. "
    "It does not prove correctness, security, safety, production readiness, or autonomous repair authority."
)


@dataclass
class RepairRecommendation:
    recommendation_id: str
    pressure_source: str
    repair_class: str
    allowed_action: str
    blocked_action: str
    required_validation: List[str]
    evidence: Dict[str, Any] = field(default_factory=dict)
    claim_boundary: str = CLAIM_BOUNDARY


@dataclass
class RepairDryRunPlan:
    plan_id: str
    recommendation_id: str
    execution_mode: str
    target_writes: List[str]
    target_writes_performed: int
    api_writes_performed: int
    git_commits_performed: int
    rollback_required: bool
    blocked_action_preservation: List[str]
    required_validation: List[str]
    claim_boundary: str = CLAIM_BOUNDARY


@dataclass
class RepairApplyGate:
    gate_id: str
    plan_id: str
    status: str
    human_authorization_required: bool
    exact_target_writes: List[str]
    rollback_entries_required: List[str]
    target_writes_performed: int
    api_writes_performed: int
    git_commits_performed: int
    claim_boundary: str = CLAIM_BOUNDARY


@dataclass
class SelfHealingReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    recommendations: List[Dict[str, Any]]
    dry_run_plans: List[Dict[str, Any]]
    apply_gates: List[Dict[str, Any]]
    dominant_pressure_source: str
    next_action: str
    claim_boundary: str = CLAIM_BOUNDARY


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _latest_unit_test_log(root: Path) -> str:
    base = root / "reports" / "human_surface"
    if not base.exists():
        return ""
    logs = sorted(base.rglob("02_unit_tests.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return ""
    return _text(logs[0])


def _add_recommendation(
    recs: List[RepairRecommendation],
    pressure_source: str,
    repair_class: str,
    allowed_action: str,
    required_validation: List[str],
    evidence: Dict[str, Any],
) -> None:
    rec_id = f"rec-{len(recs)+1:03d}-{pressure_source}"
    recs.append(RepairRecommendation(
        recommendation_id=rec_id,
        pressure_source=pressure_source,
        repair_class=repair_class,
        allowed_action=allowed_action,
        blocked_action="autonomous_target_write_without_human_authorization",
        required_validation=required_validation,
        evidence=evidence,
    ))


def detect_repair_recommendations(root: str | Path = ".") -> List[RepairRecommendation]:
    root = Path(root).resolve()
    recs: List[RepairRecommendation] = []

    nexus_sh = _text(root / "scripts" / "nexus.sh")
    nexus_ps1 = _text(root / "scripts" / "nexus.ps1")
    human_ps1 = _text(root / "scripts" / "nexus_human.ps1")
    unit_log = _latest_unit_test_log(root)

    if "FAILURE_MODE_CHART" not in nexus_sh:
        _add_recommendation(
            recs,
            "bash_failure_chart_marker_missing",
            "SCRIPT_MARKER_REPAIR",
            "restore literal FAILURE_MODE_CHART marker in scripts/nexus.sh",
            ["python -m unittest discover -s tests", "python -m nexus_gate.compiler --root . --json"],
            {"script": "scripts/nexus.sh", "detected_from": "file_scan"},
        )

    if "strict" not in nexus_sh:
        _add_recommendation(
            recs,
            "bash_strict_mode_missing",
            "SCRIPT_COMMAND_SURFACE_REPAIR",
            "restore strict command in scripts/nexus.sh",
            ["python -m unittest discover -s tests"],
            {"script": "scripts/nexus.sh", "detected_from": "file_scan"},
        )

    if "CRLF will be replaced by LF" not in human_ps1 or "LF will be replaced by CRLF" not in human_ps1:
        _add_recommendation(
            recs,
            "crlf_filter_literal_missing",
            "HUMAN_SURFACE_REPAIR",
            "restore CRLF/LF warning filter markers in scripts/nexus_human.ps1",
            ["python -m unittest discover -s tests", ".\\scripts\\nexus.ps1 human"],
            {"script": "scripts/nexus_human.ps1", "detected_from": "file_scan"},
        )

    if "nexus_gate.feedback.compile" not in nexus_ps1:
        _add_recommendation(
            recs,
            "feedback_compiler_marker_missing",
            "COMPACT_SURFACE_REPAIR",
            "restore feedback compiler marker in scripts/nexus.ps1",
            ["python -m unittest discover -s tests"],
            {"script": "scripts/nexus.ps1", "detected_from": "file_scan"},
        )

    if "FAILED (failures=" in unit_log:
        matches = re.findall(r"FAIL: ([^\n]+)", unit_log)
        if matches:
            _add_recommendation(
                recs,
                "latest_unit_test_failure",
                "TEST_FAILURE_ROUTE",
                "route latest unit-test failure into exact script/doc marker repair",
                ["python -m unittest discover -s tests"],
                {"failures": matches[:8]},
            )

    if not recs:
        _add_recommendation(
            recs,
            "no_active_repair_pressure",
            "OBSERVE_ONLY",
            "continue bounded evolution with feedback visibility",
            ["python -m unittest discover -s tests", ".\\scripts\\nexus.ps1 evolve"],
            {"state": "stable"},
        )

    return recs


def build_dry_run_plans(recommendations: List[RepairRecommendation]) -> List[RepairDryRunPlan]:
    plans: List[RepairDryRunPlan] = []
    for idx, rec in enumerate(recommendations, start=1):
        target = rec.evidence.get("script") or rec.evidence.get("target") or "none"
        plans.append(RepairDryRunPlan(
            plan_id=f"plan-{idx:03d}-{rec.repair_class.lower()}",
            recommendation_id=rec.recommendation_id,
            execution_mode="dry_run_only",
            target_writes=[] if target == "none" else [str(target)],
            target_writes_performed=0,
            api_writes_performed=0,
            git_commits_performed=0,
            rollback_required=target != "none",
            blocked_action_preservation=[
                "no_autonomous_write",
                "no_api_write",
                "no_git_commit",
                "no_memory_promotion",
                "no_tool_mutation",
            ],
            required_validation=rec.required_validation,
        ))
    return plans


def build_apply_gates(plans: List[RepairDryRunPlan]) -> List[RepairApplyGate]:
    gates: List[RepairApplyGate] = []
    for idx, plan in enumerate(plans, start=1):
        gates.append(RepairApplyGate(
            gate_id=f"gate-{idx:03d}-human-authorized-apply",
            plan_id=plan.plan_id,
            status="blocked_until_human_authorized",
            human_authorization_required=True,
            exact_target_writes=plan.target_writes,
            rollback_entries_required=plan.target_writes,
            target_writes_performed=0,
            api_writes_performed=0,
            git_commits_performed=0,
        ))
    return gates


def compile_self_healing(root: str | Path = ".") -> SelfHealingReport:
    root = Path(root).resolve()
    recs = detect_repair_recommendations(root)
    plans = build_dry_run_plans(recs)
    gates = build_apply_gates(plans)

    active = [r for r in recs if r.pressure_source != "no_active_repair_pressure"]
    status = "warn" if active else "pass"
    dominant = active[0].pressure_source if active else "none"
    next_action = (
        "Apply the provided human-authorized patch, then run .\\scripts\\nexus.ps1 evolve."
        if active
        else "No repair pressure detected. Continue with .\\scripts\\nexus.ps1 evolve."
    )

    return SelfHealingReport(
        system="NEXUS GATE",
        version="0.2.2b-self-healing",
        root=str(root),
        status=status,
        generated_at_utc=_utc(),
        recommendations=[asdict(r) for r in recs],
        dry_run_plans=[asdict(p) for p in plans],
        apply_gates=[asdict(g) for g in gates],
        dominant_pressure_source=dominant,
        next_action=next_action,
    )


def write_self_healing_report(report: SelfHealingReport, root: str | Path = ".") -> Path:
    root = Path(root).resolve()
    out = root / "reports"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data = asdict(report)
    text = json.dumps(data, indent=2)
    path = out / f"nexus_self_healing_report_{stamp}.json"
    latest = out / "nexus_self_healing_report_latest.json"
    path.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    return latest
