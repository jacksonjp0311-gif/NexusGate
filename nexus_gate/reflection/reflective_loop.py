from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


CLAIM_BOUNDARY = (
    "Reflective loop compilation is local development evidence only. It does not prove "
    "correctness, security, safety, production readiness, model understanding, or autonomous authority."
)

EXPECTED_INTERFACES = {
    "powershell_cli",
    "powershell_tui",
    "electron_hud",
    "chatgpt_handoff",
    "codex_handoff",
    "future_browser_dashboard",
    "future_local_agent",
}

EXPECTED_BLOCKED = {"self_authorize", "arbitrary_shell_commands", "bypass_evolve"}

REQUIRED_READ_SURFACES = {
    "state/ai_feedback_context_latest.json",
    "docs/feedback/FEEDBACK_LOG.md",
    "reports/nexus_feedback_interface_report_latest.json",
    "reports/nexus_self_healing_report_latest.json",
    "reports/tui/nexus_tui_ai_handoff_latest.txt",
    "reports/tui/nexus_tui_snapshot_latest.html",
    "reports/tui/nexus_tui_surface_latest.json",
    "reports/nexus_electron_preflight_report_latest.json",
    "reports/nexus_electron_smoke_report_latest.json",
}


@dataclass
class ReflectiveLoopReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    read_surfaces: list[str] = field(default_factory=list)
    write_surfaces: list[str] = field(default_factory=list)
    allowed_interfaces: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    next_action: str = ""
    claim_boundary: str = CLAIM_BOUNDARY


def _check(name: str, passed: bool, evidence: dict[str, Any], warn: bool = False) -> dict[str, Any]:
    if passed:
        status = "pass"
    else:
        status = "warn" if warn else "fail"
    return {"check": name, "status": status, "evidence": evidence}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _interface_ids(contract: dict[str, Any]) -> set[str]:
    return {str(item.get("interface_id", "")) for item in contract.get("interfaces", [])}


def _flatten(items: list[Any]) -> list[str]:
    values: list[str] = []
    for item in items:
        if isinstance(item, str):
            values.append(item)
    return values


def compile_reflective_loop(root: str | Path = ".") -> ReflectiveLoopReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    required_paths = [
        "docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md",
        "docs/interfaces/INTERFACE_ADAPTER_CONTRACT.md",
        "docs/versioning/NEXUS_LINEAGE_PROTOCOL.md",
        "state/interface_adapter_contract_index.v0.3.7.json",
        "state/nexus_lineage_manifest_latest.json",
        "docs/ui/ELECTRON_READ_CONTRACT.md",
        "state/electron_read_contract_index.v0.3.2.json",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(_check("reflective_required_paths", not missing, {"missing": missing}))

    contract = _read_json(root / "state/interface_adapter_contract_index.v0.3.7.json")
    lineage = _read_json(root / "state/nexus_lineage_manifest_latest.json")
    electron = _read_json(root / "state/electron_read_contract_index.v0.3.2.json")

    ids = _interface_ids(contract)
    checks.append(_check(
        "interface_modes_declared",
        EXPECTED_INTERFACES.issubset(ids),
        {"missing": sorted(EXPECTED_INTERFACES - ids), "declared": sorted(ids)},
    ))

    interfaces = contract.get("interfaces", [])
    read_surfaces = sorted(set(sum((_flatten(item.get("read_surfaces", [])) for item in interfaces), [])))
    write_surfaces = sorted(set(sum((_flatten(item.get("write_surfaces", [])) for item in interfaces), [])))
    blocked_actions = sorted(set(sum((_flatten(item.get("blocked_actions", [])) for item in interfaces), [])))

    checks.append(_check(
        "compressed_handoff_surfaces_declared",
        REQUIRED_READ_SURFACES.issubset(set(read_surfaces) | set(electron.get("read_surfaces", []))),
        {"missing": sorted(REQUIRED_READ_SURFACES - (set(read_surfaces) | set(electron.get("read_surfaces", []))))},
    ))

    checks.append(_check(
        "blocked_actions_declared",
        EXPECTED_BLOCKED.issubset(set(blocked_actions)),
        {"missing": sorted(EXPECTED_BLOCKED - set(blocked_actions))},
    ))

    autonomous = [
        item.get("interface_id")
        for item in interfaces
        if str(item.get("authority_level", "")).lower() in {"autonomous", "autonomous_mutation", "self_authorized"}
    ]
    checks.append(_check("no_autonomous_authority", not autonomous, {"violations": autonomous}))

    checks.append(_check(
        "lineage_tracks_versions",
        lineage.get("system_version") in {"0.3.7", "0.4.0"}
        and lineage.get("reflective_loop_version") == "0.3.7"
        and "blocked_promotions" in lineage,
        {
            "system_version": lineage.get("system_version"),
            "reflective_loop_version": lineage.get("reflective_loop_version"),
        },
    ))

    docs_text = (root / "docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md").read_text(encoding="utf-8")
    checks.append(_check(
        "reflective_doctrine_present",
        "Reflective intelligence is permitted." in docs_text
        and "Autonomous authority is not." in docs_text
        and "The loop may adapt, improvise, and overcome." in docs_text,
        {"doc": "docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md"},
    ))

    checks.append(_check(
        "claim_boundary_present",
        "autonomous authority" in contract.get("claim_boundary", "").lower()
        and "production readiness" in CLAIM_BOUNDARY,
        {"claim_boundary": CLAIM_BOUNDARY},
    ))

    status = "pass"
    if any(item["status"] == "fail" for item in checks):
        status = "fail"
    elif any(item["status"] == "warn" for item in checks):
        status = "warn"

    next_action = "Continue with .\\scripts\\nexus.ps1 evolve." if status == "pass" else "Repair reflective loop contract gaps, then rerun .\\scripts\\nexus.ps1 reflect."

    return ReflectiveLoopReport(
        system="NEXUS GATE",
        version="0.3.7-reflective-intelligence-loop",
        root=str(root),
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        read_surfaces=read_surfaces,
        write_surfaces=write_surfaces,
        allowed_interfaces=sorted(ids),
        blocked_actions=blocked_actions,
        next_action=next_action,
    )


def write_reflective_loop_report(report: ReflectiveLoopReport, root: str | Path = ".") -> Path:
    reports = Path(root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_reflective_loop_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return latest
