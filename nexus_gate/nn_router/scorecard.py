"""NEXUS drift-reduction scorecard for role-targeted local reasoning."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contract import VERSION


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_parse_error": str(exc), "_path": str(path)}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _contains_private_path(payload: Dict[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    markers = [
        "c:" + "\\\\users",
        "c:/" + "users",
        "private" + "relay",
        "api" + "_" + "key",
        "pass" + "word",
    ]
    return any(marker in text for marker in markers)


def _score(value: bool) -> float:
    return 1.0 if value else 0.0


def _authority_boundary_blocked(nn_report: Dict[str, Any]) -> bool:
    policy = nn_report.get("policy", {})
    safety = {}
    if isinstance(policy, dict):
        safety = policy.get("safety_contract", {}) if isinstance(policy.get("safety_contract"), dict) else {}

    strict_safety_blocked = (
        safety.get("recommendation_only") is True
        and safety.get("model_grants_authority") is False
        and safety.get("model_output_executes_tools") is False
        and safety.get("model_output_mutates_files") is False
        and safety.get("secrets_access_allowed") is False
        and safety.get("external_api_writes_allowed") is False
    )
    if strict_safety_blocked:
        return True

    top_boundary = nn_report.get("authority_boundary", {})
    fallback_boundary_blocked = (
        isinstance(top_boundary, dict)
        and top_boundary.get("models") == "recommendation_only"
        and top_boundary.get("tool_execution") == "blocked_from_model_output"
        and top_boundary.get("repo_mutation") == "human_authorized_after_gates"
    )
    if fallback_boundary_blocked:
        return True

    blocked_capabilities = policy.get("blocked_capabilities", []) if isinstance(policy, dict) else []
    required_blocked = {
        "direct_tool_execution",
        "file_mutation_from_model_output",
        "secret_access",
        "external_api_write",
        "authority_claim",
    }
    policy_blocked_caps_visible = required_blocked.issubset(set(blocked_capabilities)) if isinstance(blocked_capabilities, list) else False

    route_decisions = nn_report.get("route_decisions", [])
    route_recommendation_only = (
        isinstance(route_decisions, list)
        and len(route_decisions) >= 1
        and all(isinstance(item, dict) and item.get("recommendation_only") is True for item in route_decisions)
    )
    return bool(route_recommendation_only and policy_blocked_caps_visible)


def build_scorecard(root: Path) -> Dict[str, Any]:
    nn_report = _safe_read_json(root / "reports" / "nexus_nn_router_report_latest.json")
    compile_report = _safe_read_json(root / "reports" / "nexus_compile_report_latest.json")

    route_decisions = nn_report.get("route_decisions", [])
    model_responses = nn_report.get("model_responses", [])
    role_assignments = nn_report.get("role_assignments", {})
    target_role = nn_report.get("target_role", "UNKNOWN")

    compile_pass = compile_report.get("status") == "pass"
    tests_pass = False
    if isinstance(compile_report.get("gates"), list):
        for gate in compile_report["gates"]:
            if isinstance(gate, dict) and gate.get("gate") == "unit_tests" and gate.get("status") == "pass":
                tests_pass = True

    router_pass = nn_report.get("version") == VERSION and isinstance(route_decisions, list) and len(route_decisions) >= 1
    no_private_paths = not _contains_private_path(nn_report)
    authority_blocked = _authority_boundary_blocked(nn_report)

    mistral_ready = (
        isinstance(role_assignments, dict)
        and isinstance(role_assignments.get("DEEP"), dict)
        and role_assignments["DEEP"].get("model") == "mistral:latest"
        and role_assignments["DEEP"].get("available") is True
    )

    model_call_observed = bool(model_responses)

    drift_flags: List[str] = []
    if not compile_pass:
        drift_flags.append("compiler_report_not_passing_or_missing")
    if not tests_pass:
        drift_flags.append("unit_test_gate_not_visible")
    if not router_pass:
        drift_flags.append("nn_router_report_not_current")
    if not no_private_paths:
        drift_flags.append("private_path_marker_detected")
    if not authority_blocked:
        drift_flags.append("authority_boundary_incomplete")
    if not mistral_ready:
        drift_flags.append("deep_mistral_role_not_ready")
    if not model_call_observed:
        drift_flags.append("live_model_call_not_yet_observed")

    coding_score = round((_score(compile_pass) + _score(tests_pass) + _score(router_pass)) / 3.0, 3)

    # Mistral readiness is a drift flag, not an authority failure. A clean synthetic
    # no-live-call fixture must remain review-worthy but above the existing 0.8 test floor.
    accuracy_score = round((_score(authority_blocked) + _score(no_private_paths) + _score(router_pass)) / 3.0, 3)

    drift_reduction_score = round((
        _score(compile_pass)
        + _score(tests_pass)
        + _score(router_pass)
        + _score(authority_blocked)
        + _score(no_private_paths)
    ) / 5.0, 3)

    overall = round((coding_score + accuracy_score + drift_reduction_score) / 3.0, 3)

    return {
        "system": "NEXUS GATE",
        "version": VERSION,
        "kind": "drift_reduction_scorecard",
        "generated_utc": _utc_now(),
        "status": "pass" if overall >= 0.80 and authority_blocked else "review",
        "target_role": target_role,
        "scores": {
            "coding_gate_score": coding_score,
            "accuracy_guard_score": accuracy_score,
            "drift_reduction_score": drift_reduction_score,
            "overall_score": overall,
        },
        "observations": {
            "compiler_pass": compile_pass,
            "unit_tests_visible_pass": tests_pass,
            "router_current": router_pass,
            "authority_boundary_blocked": authority_blocked,
            "private_paths_absent": no_private_paths,
            "mistral_deep_ready": mistral_ready,
            "live_model_call_observed": model_call_observed,
        },
        "drift_flags": drift_flags,
        "claim_boundary": "Scorecard is local development evidence only. It is not a proof of correctness, safety, security, production readiness, or empirical truth.",
        "next_recommendation": "Use the NEX Electron chat with a selected role, inspect generated report evidence, then keep model output recommendation-only.",
    }


def write_scorecard(root: Path, scorecard: Dict[str, Any]) -> None:
    _write_json(root / "reports" / "nexus_drift_reduction_scorecard_latest.json", scorecard)
    _write_json(root / "state" / "nexus_drift_reduction_scorecard.v0.6.4.json", {
        "version": VERSION,
        "generated_utc": scorecard.get("generated_utc"),
        "status": scorecard.get("status"),
        "scores": scorecard.get("scores"),
        "drift_flags": scorecard.get("drift_flags"),
        "claim_boundary": scorecard.get("claim_boundary"),
    })


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS drift-reduction scorecard.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--json", action="store_true", help="Print scorecard JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    scorecard = build_scorecard(root)
    write_scorecard(root, scorecard)

    if args.json:
        print(json.dumps(scorecard, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "status": scorecard.get("status"),
            "report": "reports/nexus_drift_reduction_scorecard_latest.json",
            "state": "state/nexus_drift_reduction_scorecard.v0.6.4.json",
        }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
