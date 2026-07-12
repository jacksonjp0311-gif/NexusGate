from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.decision.arbiter import arbitrate_recommendations
from nexus_gate.coherence.states import classify_coherence
from nexus_gate.lattice.triadic import build_triadic_lattice, apply_lattice_alignment
from nexus_gate.loops.wounds import has_active_wound
from nexus_gate.state.snapshot import capture_repository_snapshot, packet_is_fresh


VERSION = "2.5.0"
SCHEMA = "NEXUS_DECISION_ENVELOPE.v2.5.0"
REPORT_LATEST = Path("reports") / "nexus_decision_envelope_latest.json"
STATE_LATEST = Path("state") / "decision" / "nexus_decision_envelope_latest.json"

CLAIM_BOUNDARY = (
    "The NEXUS Decision Envelope is local development evidence only. It gathers "
    "origin, memory, runtime, wound, certificate, and git-scope evidence into a "
    "recommendation-only packet. It does not execute the recommendation, prove "
    "correctness, safety, security, production readiness, model understanding, "
    "or grant autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "execute_selected_action",
    "bypass_final_evolve",
    "git_write",
    "arbitrary_shell_commands",
    "external_api_writes",
    "secret_access",
    "memory_promotion_without_evidence",
]

READ_SURFACES = [
    "state/nexus_origin_manifest_latest.json",
    "reports/nexus_origin_seal_latest.json",
    "reports/nexus_cortex_refresh_report_latest.json",
    "reports/nexus_cortex_gate_latest.json",
    "reports/nexus_predictive_memory_orchestrator_latest.json",
    "reports/nexus_predictive_evolve_plan_latest.json",
    "reports/nexus_predictive_gate_timing_latest.json",
    "reports/nexus_certificate_resume_report_latest.json",
    "state/loops/nexus_wound_compression_latest.json",
    "reports/nexus_preflight_optimizer_latest.json",
    "state/algorithms/nexus_algorithm_cards_latest.json",
    "state/discoveries/nexus_discovery_cards_latest.json",
    "reports/nexus_coherence_field_latest.json",
    "state/coherence/arbiter_calibration_latest.json",
    "state/coherence/pressure_memory_latest.json",
    "reports/nexus_triadic_lattice_latest.json",
    "state/lattice/nexus_triadic_lattice_latest.json",
    "git status --short",
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


def _packet_hash(packet: Any) -> str:
    encoded = json.dumps(packet, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _git_scope(root: Path) -> dict[str, Any]:
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
    entries = [line for line in proc.stdout.splitlines() if line.strip()]
    return {
        "status": "pass" if proc.returncode == 0 else "warn",
        "dirty_count": len(entries),
        "entries": entries[:80],
        "truncated": len(entries) > 80,
    }


def _recommendation(
    source: str,
    action: str,
    command: str,
    why: str,
    severity: str = "info",
    confidence: float = 0.7,
    estimated_cost: str = "bounded",
    blocking_conditions: list[str] | None = None,
    source_packet: Any | None = None,
    repository_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    freshness = None
    if isinstance(source_packet, dict) and repository_snapshot:
        freshness = {
            "fresh": packet_is_fresh(source_packet, repository_snapshot),
            "rule": "repository_commit + source_status_hash + input_snapshot_hash",
        }
    return {
        "source": source,
        "action": action,
        "command": command,
        "why": why,
        "severity": severity,
        "confidence": confidence,
        "estimated_cost": estimated_cost,
        "blocking_conditions": blocking_conditions or [],
        "source_packet_hash": _packet_hash(source_packet) if source_packet is not None else None,
        "source_packet_freshness": freshness,
    }


def _origin_summary(origin_manifest: dict[str, Any], origin_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_version": origin_manifest.get("product_version") or origin_report.get("product_version"),
        "product_phase": origin_manifest.get("product_phase") or origin_report.get("product_phase"),
        "origin_manifest_hash": origin_manifest.get("origin_manifest_hash") or origin_report.get("origin_manifest_hash"),
        "commit": origin_manifest.get("current_commit") or origin_report.get("current_commit"),
        "status": origin_report.get("status", "unknown"),
        "schema": origin_report.get("schema") or origin_manifest.get("schema"),
    }


def _memory_summary(
    predictive_memory: dict[str, Any],
    cortex_refresh: dict[str, Any],
    algorithms: dict[str, Any],
    discoveries: dict[str, Any],
) -> dict[str, Any]:
    rec = predictive_memory.get("recommendation") or {}
    return {
        "predictive_memory_status": predictive_memory.get("status", "unknown"),
        "predictive_memory_next_loop": rec.get("recommended_next_loop"),
        "predictive_memory_next_command": rec.get("recommended_next_command"),
        "cortex_refresh_status": cortex_refresh.get("status", "unknown"),
        "cortex_authority": cortex_refresh.get("authority") or cortex_refresh.get("authority_boundary"),
        "algorithm_cards": algorithms.get("card_count", 0),
        "discovery_cards": discoveries.get("card_count", 0),
    }


def _risk_summary(
    git_scope: dict[str, Any],
    timing: dict[str, Any],
    wound: dict[str, Any],
    certificate_resume: dict[str, Any],
) -> dict[str, Any]:
    high_timing = [
        item for item in timing.get("runtime_pressure", [])
        if item.get("pressure_level") == "high"
    ]
    return {
        "dirty_count": git_scope.get("dirty_count"),
        "runtime_pressure": "high" if high_timing else timing.get("status", "unknown"),
        "slowest_gate": high_timing[0].get("step") if high_timing else None,
        "active_wound_key": wound.get("active_wound_key"),
        "certificate_resume_gate": certificate_resume.get("recommended_resume_gate"),
    }


def _build_recommendations(
    origin_report: dict[str, Any],
    predictive_memory: dict[str, Any],
    predictive_evolve: dict[str, Any],
    timing: dict[str, Any],
    wound: dict[str, Any],
    certificate_resume: dict[str, Any],
    preflight: dict[str, Any],
    git_scope: dict[str, Any],
    repository_snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    if origin_report.get("status") not in {"pass", "warn"}:
        recommendations.append(_recommendation(
            "origin-seal",
            "seal_product_origin",
            ".\\scripts\\nexus.ps1 origin-seal",
            "Origin evidence is missing or failed; bootstrap starts by restoring product identity.",
            "critical",
            0.95,
            "short",
            source_packet=origin_report,
            repository_snapshot=repository_snapshot,
        ))
    if has_active_wound(wound):
        recommendations.append(_recommendation(
            "wound-compression",
            "compress_active_wound",
            '.\\scripts\\nexus.ps1 wound-compress -Tag "decision envelope active wound"',
            "An active wound is visible; preserve green gates and focus the repair surface.",
            "high",
            0.9,
            "medium",
            source_packet=wound,
            repository_snapshot=repository_snapshot,
        ))
    memory_rec = predictive_memory.get("recommendation") or {}
    memory_command = memory_rec.get("recommended_next_command")
    if memory_command:
        recommendations.append(_recommendation(
            "predictive-memory",
            memory_rec.get("recommended_next_loop") or "memory_aware_next_step",
            memory_command,
            memory_rec.get("why") or "Predictive Memory produced a memory-aware next step.",
            "high" if predictive_memory.get("status") == "warn" else "medium",
            0.84,
            "bounded",
            source_packet=predictive_memory,
            repository_snapshot=repository_snapshot,
        ))
    if git_scope.get("dirty_count", 0):
        recommendations.append(_recommendation(
            "git-scope",
            "inspect_dirty_scope",
            '.\\scripts\\nexus.ps1 preflight-json -Tag "decision envelope dirty scope"',
            "The working tree is dirty; inspect scope before compounding changes or staging.",
            "medium",
            0.82,
            "short",
            source_packet=git_scope,
            repository_snapshot=repository_snapshot,
        ))
    if certificate_resume.get("recommended_resume_gate"):
        recommendations.append(_recommendation(
            "certificate-resume",
            "recommend_resume_point",
            ".\\scripts\\nexus.ps1 certificate-resume",
            f"Certificate Resume recommends starting from {certificate_resume.get('recommended_resume_gate')}.",
            "medium",
            0.75,
            "short",
            source_packet=certificate_resume,
            repository_snapshot=repository_snapshot,
        ))
    high_timing = [
        item for item in timing.get("runtime_pressure", [])
        if item.get("pressure_level") == "high"
    ]
    if high_timing:
        recommendations.append(_recommendation(
            "predictive-timing",
            "plan_runtime_pressure",
            ".\\scripts\\nexus.ps1 predictive-evolve",
            f"{high_timing[0].get('step')} has high runtime pressure; plan bounded validation before full evolve.",
            "medium",
            0.72,
            "short",
            source_packet=timing,
            repository_snapshot=repository_snapshot,
        ))
    plan = predictive_evolve.get("recommended_plan") or []
    next_step = next((step for step in plan if not step.get("required_before_commit")), None)
    if next_step:
        recommendations.append(_recommendation(
            "predictive-evolve",
            next_step.get("step_id", "predictive_evolve_step"),
            next_step.get("command", ".\\scripts\\nexus.ps1 predictive-evolve"),
            "Predictive Evolve selected the cheapest useful non-final gate.",
            "info",
            0.68,
            "bounded",
            source_packet=predictive_evolve,
            repository_snapshot=repository_snapshot,
        ))
    if preflight.get("status") == "fail":
        recommendations.append(_recommendation(
            "preflight",
            "repair_preflight_failure",
            '.\\scripts\\nexus.ps1 wound-compress -Tag "decision envelope preflight failure"',
            "Preflight reports failed evidence; route into wound compression before mutation.",
            "high",
            0.86,
            "medium",
            source_packet=preflight,
            repository_snapshot=repository_snapshot,
        ))
    recommendations.append(_recommendation(
        "final-seal",
        "run_final_evolve_before_commit",
        ".\\scripts\\nexus.ps1 evolve",
        "Final evolve remains required before any durable commit or push.",
        "required",
        1.0,
        "long",
        ["never_skip_before_commit"],
    ))
    return recommendations


def _select_action(
    recommendations: list[dict[str, Any]],
    coherence: dict[str, Any],
    calibration: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    arbiter = arbitrate_recommendations(recommendations, coherence, calibration)
    selected = arbiter["selected"]
    command = selected["command"]
    command_registry_id = None
    if "cortex-refresh" in command or selected["action"] == "cortex-refresh":
        command_registry_id = "nexus.cortex-refresh"
    elif "predictive-memory" in command:
        command_registry_id = "nexus.predictive-memory"
    elif "origin-seal" in command:
        command_registry_id = "nexus.origin-seal"
    elif "epoch-seal" in command:
        command_registry_id = "nexus.epoch-seal"
    elif "distill" in command:
        command_registry_id = "nexus.distill"
    elif "coherence-field" in command:
        command_registry_id = "nexus.coherence-field"
    elif "decision-envelope" in command:
        command_registry_id = "nexus.decision-envelope"
    elif "runtime-hygiene" in command:
        command_registry_id = "nexus.runtime-hygiene"
    return {
        "source": selected["source"],
        "next_loop": selected["action"],
        "command": command,
        "command_registry_id": command_registry_id,
        "normalized_arguments": {},
        "arguments_hash": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "authorization_required": True,
        "execution_status": "not_executed",
        "why": selected["why"],
        "arbiter_score": selected["arbiter_score"],
        "requires_human_authorization": True,
        "requires_final_evolve_before_commit": True,
        "recommendation_only": True,
    }, arbiter


def build_decision_envelope(root: str | Path, intent: str = "") -> dict[str, Any]:
    root_path = Path(root).resolve()
    repository_snapshot = capture_repository_snapshot(root_path, READ_SURFACES)
    origin_manifest = _read_json(root_path / "state" / "nexus_origin_manifest_latest.json", {})
    origin_report = _read_json(root_path / "reports" / "nexus_origin_seal_latest.json", {})
    cortex_refresh = _read_json(root_path / "reports" / "nexus_cortex_refresh_report_latest.json", {})
    cortex_gate = _read_json(root_path / "reports" / "nexus_cortex_gate_latest.json", {})
    predictive_memory = _read_json(root_path / "reports" / "nexus_predictive_memory_orchestrator_latest.json", {})
    predictive_evolve = _read_json(root_path / "reports" / "nexus_predictive_evolve_plan_latest.json", {})
    timing = _read_json(root_path / "reports" / "nexus_predictive_gate_timing_latest.json", {})
    certificate_resume = _read_json(root_path / "reports" / "nexus_certificate_resume_report_latest.json", {})
    wound = _read_json(root_path / "state" / "loops" / "nexus_wound_compression_latest.json", {})
    preflight = _read_json(root_path / "reports" / "nexus_preflight_optimizer_latest.json", {})
    algorithms = _read_json(root_path / "state" / "algorithms" / "nexus_algorithm_cards_latest.json", {})
    discoveries = _read_json(root_path / "state" / "discoveries" / "nexus_discovery_cards_latest.json", {})
    coherence = _read_json(root_path / "reports" / "nexus_coherence_field_latest.json", {})
    calibration = _read_json(root_path / "state" / "coherence" / "arbiter_calibration_latest.json", {})
    pressure_memory = _read_json(root_path / "state" / "coherence" / "pressure_memory_latest.json", {})
    git_scope = _git_scope(root_path)

    recommendations = _build_recommendations(
        origin_report,
        predictive_memory,
        predictive_evolve,
        timing,
        wound,
        certificate_resume,
        preflight,
        git_scope,
        repository_snapshot,
    )
    raw_score = (coherence.get("coherence") or {}).get("score")
    coherence_state = classify_coherence(raw_score)
    if coherence.get("status") == "fail" or coherence_state.value in {"critical", "degraded"}:
        recommendations.append(_recommendation(
            "coherence-field",
            "restore_coherence_field",
            ".\\scripts\\nexus.ps1 coherence-field",
            "Coherence Field pressure is high; refresh field state before selecting mutation routes.",
            "high",
            0.88,
            "short",
            source_packet=coherence,
            repository_snapshot=repository_snapshot,
        ))
    triadic_lattice = build_triadic_lattice(root_path, recommendations, repository_snapshot)
    recommendations = apply_lattice_alignment(recommendations, triadic_lattice)
    selected, arbiter = _select_action(recommendations, coherence, calibration)
    missing = [
        rel for rel in READ_SURFACES
        if not rel.startswith("git ") and not (root_path / rel).exists()
    ]
    warnings = []
    if missing:
        warnings.append("missing_read_surfaces")
    if git_scope.get("dirty_count", 0):
        warnings.append("dirty_scope")
    if selected["source"] != "final-seal":
        warnings.append("bounded_next_action_pending")
    status = "warn" if warnings else "pass"

    return {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "phase": "Triadic Geometric Lattice",
        "mode": "triadic_lattice_decision_envelope",
        "status": status,
        "generated_at_utc": _utc(),
        "intent": intent,
        "repository_snapshot": repository_snapshot,
        "origin": _origin_summary(origin_manifest, origin_report),
        "evidence": [
            {"surface": rel, "exists": False if rel in missing else True}
            for rel in READ_SURFACES
        ],
        "memory": _memory_summary(predictive_memory, cortex_refresh or cortex_gate, algorithms, discoveries),
        "authority": {
            "recommendation_only": True,
            "autonomous_authority": False,
            "execution_enabled": False,
            "git_write_enabled": False,
            "final_evolve_required_before_commit": True,
            "human_authorization_required_for_mutation": True,
        },
        "risk": _risk_summary(git_scope, timing, wound, certificate_resume),
        "coherence_input": {
            "status": coherence.get("status", "unknown"),
            "score": (coherence.get("coherence") or {}).get("score"),
            "state": coherence_state.value,
            "lineage_entropy": (coherence.get("coherence") or {}).get("lineage_entropy"),
            "field_state": (coherence.get("coherence") or {}).get("field_state"),
        },
        "outcome_awareness": {
            "calibration_schema": calibration.get("schema"),
            "pressure_memory_schema": pressure_memory.get("schema"),
            "pressure_trend": pressure_memory.get("trend"),
            "latest_coherence_score": pressure_memory.get("latest_coherence_score"),
        },
        "triadic_lattice": {
            "schema": triadic_lattice.get("schema"),
            "status": triadic_lattice.get("status"),
            "average_alignment": triadic_lattice.get("average_alignment"),
            "selected_hint": triadic_lattice.get("selected_hint"),
            "triad": triadic_lattice.get("triad"),
            "lattice_packet_hash": triadic_lattice.get("lattice_packet_hash"),
        },
        "wounds": {
            "active_wound_key": wound.get("active_wound_key"),
            "status": wound.get("status", "unknown"),
        },
        "certificates": {
            "recommended_resume_gate": certificate_resume.get("recommended_resume_gate"),
            "status": certificate_resume.get("status", "unknown"),
        },
        "recommendations": recommendations,
        "arbiter": arbiter,
        "selected_action": selected,
        "warnings": warnings,
        "blocked_actions": BLOCKED_ACTIONS,
        "read_surfaces": READ_SURFACES,
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            STATE_LATEST.as_posix(),
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_decision_envelope(root: str | Path, intent: str = "") -> dict[str, Any]:
    root_path = Path(root).resolve()
    packet = build_decision_envelope(root_path, intent=intent)
    for rel in (REPORT_LATEST, STATE_LATEST):
        _write_json(root_path / rel, packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the NEXUS canonical decision envelope.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Self-bootstrap NEXUS decision envelope.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_decision_envelope(args.root, intent=args.intent)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        selected = packet.get("selected_action", {})
        print(f"NEXUS decision envelope: {packet['status']} -> {selected.get('command')}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
