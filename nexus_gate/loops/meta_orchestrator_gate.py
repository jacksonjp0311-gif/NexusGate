from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1.1.3"
SCHEMA = "NEXUS_META_ORCHESTRATOR_GATE.v1.1.3"
# Compatibility marker: predictive-gate-timing now routes through predictive-evolve.
REPORT_LATEST = Path("reports") / "nexus_meta_orchestrator_gate_latest.json"
REPORT_VERSIONED = Path("reports") / "nexus_meta_orchestrator_gate.v1.1.3.json"
STATE_VERSIONED = Path("state") / "loops" / "nexus_meta_orchestrator_gate.v1.1.3.json"

READ_SURFACES = [
    "state/loops/nexus_toolbelt_latest.json",
    "reports/nexus_preflight_optimizer_latest.json",
    "state/loops/nexus_wound_compression_latest.json",
    "reports/nexus_phi_gate_supervisor_report_latest.json",
    "reports/nexus_compile_report_latest.json",
    "reports/nexus_predictive_gate_timing_latest.json",
    "reports/nexus_predictive_evolve_plan_latest.json",
    "reports/nexus_predictive_memory_orchestrator_latest.json",
    "reports/nexus_certificate_resume_report_latest.json",
]

BLOCKED_ACTIONS = [
    "autonomous_authority",
    "arbitrary_shell_commands",
    "self_authorize",
    "git_stage_all",
    "git_commit_without_passing_gates",
    "git_push_without_human_intent",
    "external_api_writes",
    "secret_access",
    "repo_mutation_from_ui",
]

AUTHORITY_BOUNDARY = {
    "repo_mutation_enabled": False,
    "arbitrary_shell_execution_enabled": False,
    "autonomous_authority": False,
    "git_write_enabled": False,
    "network_write_enabled": False,
    "secret_access_enabled": False,
    "ui_authority_enabled": False,
    "recommendation_only": True,
}

CLAIM_BOUNDARY = (
    "Meta-Orchestrator Gate compilation is local development evidence only. "
    "It recommends a bounded loop sequence and exposes HUD-readable panels; "
    "it does not prove correctness, safety, security, production readiness, "
    "model understanding, or autonomous authority."
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(_read_text(path))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_status(root: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return {"status": "warn", "dirty_count": None, "entries": [], "error": str(exc)}
    entries = [line for line in (proc.stdout or "").splitlines() if line.strip()]
    return {
        "status": "pass" if proc.returncode == 0 else "warn",
        "dirty_count": len(entries),
        "entries": entries[:40],
        "truncated": len(entries) > 40,
    }


def _compact_panel(panel_id: str, title: str, status: str, summary: str, details: Any) -> dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": status,
        "summary": summary,
        "details": details,
    }


def _surface_status(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {
        "path": rel,
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def _derive_recommendation(
    preflight: dict[str, Any],
    wound: dict[str, Any],
    phi: dict[str, Any],
    timing: dict[str, Any],
    predictive_evolve: dict[str, Any],
    predictive_memory: dict[str, Any],
    certificate_resume: dict[str, Any],
    git_info: dict[str, Any],
) -> dict[str, Any]:
    if git_info.get("dirty_count", 0):
        return {
            "next_loop": "scope-hygiene",
            "next_command": '.\\scripts\\nexus.ps1 preflight-json -Tag "scope dirty origin-seal"',
            "why": "Working tree has uncommitted residue; preserve intended-file staging before compounding.",
        }
    if preflight.get("status") == "fail":
        return {
            "next_loop": "wound-indexed-resume",
            "next_command": '.\\scripts\\nexus.ps1 wound-compress -Tag "preflight failure"',
            "why": "Preflight has failed gates; compress the active wound before mutation.",
        }
    if wound.get("status") == "fail" or wound.get("active_wound_key"):
        return {
            "next_loop": "compiler-wound-focus",
            "next_command": '.\\scripts\\nexus.ps1 phi-gate-compile',
            "why": "An active wound exists; verify the Phi gate supervisor surface before evolving.",
        }
    if phi.get("status") not in {"pass", "warn"}:
        return {
            "next_loop": "phi-gate-seal",
            "next_command": ".\\scripts\\nexus.ps1 phi-gate-compile",
            "why": "Phi Gate Supervisor compiler evidence is missing or failed.",
        }
    high_timing = [
        item for item in timing.get("runtime_pressure", [])
        if item.get("pressure_level") == "high"
    ]
    if high_timing:
        return {
            "next_loop": "predictive-evolve",
            "next_command": ".\\scripts\\nexus.ps1 predictive-evolve",
            "why": f"{high_timing[0].get('step')} has high runtime pressure; compile a dry-run next-gate plan before full evolve.",
        }
    if certificate_resume.get("recommended_resume_gate"):
        return {
            "next_loop": "certificate-resume",
            "next_command": ".\\scripts\\nexus.ps1 certificate-resume",
            "why": f"Certificate Resume recommends resuming from {certificate_resume.get('recommended_resume_gate')}.",
        }
    memory_rec = predictive_memory.get("recommendation") or {}
    memory_command = memory_rec.get("recommended_next_command")
    if predictive_memory.get("status") in {"pass", "warn"} and memory_command:
        return {
            "next_loop": memory_rec.get("recommended_next_loop") or "predictive-memory",
            "next_command": memory_command,
            "why": f"Predictive Memory selected this from Cortex/card/timing evidence: {memory_rec.get('why')}",
        }
    if predictive_evolve.get("status") in {"pass", "warn"}:
        plan = predictive_evolve.get("recommended_plan") or []
        next_step = next((step for step in plan if not step.get("required_before_commit")), None)
        if next_step:
            return {
                "next_loop": "predictive-evolve",
                "next_command": next_step.get("command") or ".\\scripts\\nexus.ps1 predictive-evolve",
                "why": "Predictive Evolve has a current dry-run plan for the cheapest next gate.",
            }
    return {
        "next_loop": "evolution-radar",
        "next_command": ".\\scripts\\nexus.ps1 evolve",
        "why": "No active gate wound is visible; run the normal evolve chain.",
    }


def build_meta_orchestrator_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    toolbelt = _read_json(root / "state" / "loops" / "nexus_toolbelt_latest.json", {})
    preflight = _read_json(root / "reports" / "nexus_preflight_optimizer_latest.json", {})
    wound = _read_json(root / "state" / "loops" / "nexus_wound_compression_latest.json", {})
    phi = _read_json(root / "reports" / "nexus_phi_gate_supervisor_report_latest.json", {})
    timing = _read_json(root / "reports" / "nexus_predictive_gate_timing_latest.json", {})
    predictive_evolve = _read_json(root / "reports" / "nexus_predictive_evolve_plan_latest.json", {})
    predictive_memory = _read_json(root / "reports" / "nexus_predictive_memory_orchestrator_latest.json", {})
    certificate_resume = _read_json(root / "reports" / "nexus_certificate_resume_report_latest.json", {})
    compile_report = _read_json(root / "reports" / "nexus_compile_report_latest.json", {})
    git_info = _git_status(root)
    recommendation = _derive_recommendation(preflight, wound, phi, timing, predictive_evolve, predictive_memory, certificate_resume, git_info)

    panels = [
        _compact_panel(
            "toolbelt",
            "Toolbelt",
            toolbelt.get("status", "unknown"),
            toolbelt.get("recommended_next_loop") or toolbelt.get("next_command") or "Toolbelt packet not emitted yet.",
            {
                "version": toolbelt.get("version"),
                "recommended_next_command": toolbelt.get("recommended_next_command") or toolbelt.get("next_command"),
                "boundary": toolbelt.get("boundary"),
            },
        ),
        _compact_panel(
            "preflight",
            "Preflight",
            preflight.get("status", "unknown"),
            preflight.get("recommended_next_loop") or "Preflight packet not emitted yet.",
            {
                "failed_gates": preflight.get("failed_preflight_gates") or [],
                "warning_gates": preflight.get("warning_preflight_gates") or [],
                "recommended_next_command": preflight.get("recommended_next_command"),
            },
        ),
        _compact_panel(
            "wound",
            "Wound Compression",
            wound.get("status", "unknown"),
            wound.get("active_wound_key") or wound.get("recommended_next_loop") or "No compressed wound visible.",
            {
                "active_wound": wound.get("active_wound"),
                "truth_rule": wound.get("truth_rule"),
                "boundary": wound.get("boundary"),
            },
        ),
        _compact_panel(
            "phi_supervisor",
            "Phi Gate Supervisor",
            phi.get("status", "unknown"),
            phi.get("next_action") or "Phi supervisor compiler packet not emitted yet.",
            {
                "version": phi.get("version"),
                "failed_checks": phi.get("failed_checks") or [],
                "allowed_repair_lanes": phi.get("allowed_repair_lanes") or [],
            },
        ),
        _compact_panel(
            "predictive_timing",
            "Predictive Timing",
            timing.get("status", "unknown"),
            (timing.get("recommendation") or {}).get("why") or "Predictive timing packet not emitted yet.",
            {
                "runtime_pressure": timing.get("runtime_pressure") or [],
                "recommended_next_command": (timing.get("recommendation") or {}).get("recommended_next_command"),
                "claim_boundary": timing.get("claim_boundary"),
            },
        ),
        _compact_panel(
            "predictive_evolve",
            "Predictive Evolve",
            predictive_evolve.get("status", "unknown"),
            (predictive_evolve.get("gate_selection_policy") or {}).get("why") or "Predictive evolve plan not emitted yet.",
            {
                "recommended_plan": predictive_evolve.get("recommended_plan") or [],
                "final_evolve_required_before_commit": predictive_evolve.get("final_evolve_required_before_commit"),
                "claim_boundary": predictive_evolve.get("claim_boundary"),
            },
        ),
        _compact_panel(
            "predictive_memory",
            "Predictive Memory",
            predictive_memory.get("status", "unknown"),
            (predictive_memory.get("recommendation") or {}).get("why") or "Predictive memory packet not emitted yet.",
            {
                "cortex_memory": predictive_memory.get("cortex_memory") or {},
                "card_memory": predictive_memory.get("card_memory") or {},
                "recommended_next_command": (predictive_memory.get("recommendation") or {}).get("recommended_next_command"),
                "claim_boundary": predictive_memory.get("claim_boundary"),
            },
        ),
        _compact_panel(
            "certificate_resume",
            "Certificate Resume",
            certificate_resume.get("status", "unknown"),
            certificate_resume.get("recommended_resume_gate") or "No resume wound visible.",
            {
                "certificate_count": certificate_resume.get("certificate_count"),
                "recommended_next_command": certificate_resume.get("recommended_next_command"),
                "final_evolve_required_before_commit": certificate_resume.get("final_evolve_required_before_commit"),
                "claim_boundary": certificate_resume.get("claim_boundary"),
            },
        ),
        _compact_panel(
            "repo_scope",
            "Repo Scope",
            git_info.get("status", "unknown"),
            f"{git_info.get('dirty_count')} dirty entries visible.",
            git_info,
        ),
    ]

    checks = [
        {"name": "read surface exists", "status": "pass" if item["exists"] else "warn", **item}
        for item in (_surface_status(root, rel) for rel in READ_SURFACES)
    ]
    checks.append({
        "name": "blocked actions declared",
        "status": "pass" if {"self_authorize", "arbitrary_shell_commands"}.issubset(set(BLOCKED_ACTIONS)) else "fail",
        "blocked_actions": BLOCKED_ACTIONS,
    })
    checks.append({
        "name": "recommendation only boundary",
        "status": "pass" if AUTHORITY_BOUNDARY["recommendation_only"] and not AUTHORITY_BOUNDARY["autonomous_authority"] else "fail",
        "authority_boundary": AUTHORITY_BOUNDARY,
    })
    failed = [check for check in checks if check.get("status") == "fail"]
    warned = [check for check in checks if check.get("status") == "warn"]

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "meta_orchestrator_gate",
        "status": "fail" if failed else "warn" if warned else "pass",
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "recommended_sequence": [
            "toolbelt",
            "preflight-json",
            "wound-compress",
            "phi-gate-compile",
            "selected-gate",
        ],
        "recommended_next_loop": recommendation["next_loop"],
        "recommended_next_command": recommendation["next_command"],
        "why": recommendation["why"],
        "panels": panels,
        "checks": checks,
        "read_surfaces": READ_SURFACES,
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            REPORT_VERSIONED.as_posix(),
            STATE_VERSIONED.as_posix(),
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_meta_orchestrator_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_meta_orchestrator_packet(root, intent)
    _write_json(root / REPORT_LATEST, packet)
    _write_json(root / REPORT_VERSIONED, packet)
    _write_json(root / STATE_VERSIONED, {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "generated_utc": packet["generated_utc"],
        "recommended_next_loop": packet["recommended_next_loop"],
        "recommended_next_command": packet["recommended_next_command"],
        "blocked_actions": packet["blocked_actions"],
        "claim_boundary": packet["claim_boundary"],
    })
    return packet


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS META-ORCHESTRATOR GATE",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Next loop: {packet.get('recommended_next_loop')}",
        f"Next command: {packet.get('recommended_next_command')}",
        f"Why: {packet.get('why')}",
        "Boundary: recommendation-only; UI reads panels; human authorizes durable mutation.",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS Meta-Orchestrator Gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_meta_orchestrator_packet(args.root, args.intent)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
