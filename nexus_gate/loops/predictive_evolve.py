from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.loops.predictive_timing import build_predictive_timing_packet


VERSION = "1.1.7"
SCHEMA = "NEXUS_PREDICTIVE_EVOLVE_PLAN.v1.1.7"
REPORT_LATEST = Path("reports") / "nexus_predictive_evolve_plan_latest.json"
STATE_LATEST = Path("state") / "loops" / "nexus_predictive_evolve_plan_latest.json"

CLAIM_BOUNDARY = (
    "Predictive Evolve is a local dry-run planning surface only. It may inspect "
    "runtime pressure and changed-file scope to recommend cheaper next gates, but "
    "it does not mutate the repository, execute the plan, prove correctness, prove "
    "safety/security/production readiness, or authorize skipping final evolve."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "bypass_evolve",
    "skip_final_evolve_before_commit",
    "run_mutating_commands",
    "arbitrary_shell_commands",
    "git_write",
    "external_api_writes",
    "hide_failures",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _plan_steps(timing: dict[str, Any]) -> list[dict[str, Any]]:
    gate_policy = timing.get("gate_selection_policy", {})
    recommendation = timing.get("recommendation", {})
    recommended_command = gate_policy.get("recommended_command") or recommendation.get("recommended_next_command")
    policy_id = gate_policy.get("policy_id", "normal-evolve-when-ready")

    steps: list[dict[str, Any]] = [
        {
            "order": 1,
            "step_id": "predictive-timing",
            "command": ".\\scripts\\nexus.ps1 predictive-timing",
            "purpose": "Refresh timing pressure, scope classification, and adaptive timeout recommendations.",
            "required_before_commit": False,
            "dry_run_only": True,
        }
    ]

    seen_commands = {steps[0]["command"]}
    if (
        recommended_command
        and recommended_command != ".\\scripts\\nexus.ps1 evolve"
        and recommended_command not in seen_commands
    ):
        steps.append(
            {
                "order": len(steps) + 1,
                "step_id": policy_id,
                "command": recommended_command,
                "purpose": gate_policy.get("why") or recommendation.get("why") or "Run the cheapest valid next gate.",
                "required_before_commit": False,
                "dry_run_only": False,
            }
        )
        seen_commands.add(recommended_command)

    steps.append(
        {
            "order": len(steps) + 1,
            "step_id": "final-evolve-seal",
            "command": ".\\scripts\\nexus.ps1 evolve",
            "purpose": "Final local evidence seal required before commit or push.",
            "required_before_commit": True,
            "dry_run_only": False,
        }
    )
    return steps


def _next_evolution_candidates(timing: dict[str, Any]) -> list[dict[str, str]]:
    pressure = timing.get("runtime_pressure") or []
    top = pressure[0] if pressure else {}
    return [
        {
            "candidate_id": "hud-runtime-pressure",
            "summary": "Expose runtime pressure, slowest gate, recommended next gate, and timeout budget in the System Monitor / Meta-Orchestrator HUD.",
        },
        {
            "candidate_id": "confidence-windows",
            "summary": "Add EWMA and confidence-window estimates so timeouts react to trend without overfitting one slow run.",
        },
        {
            "candidate_id": "certificate-resume",
            "summary": "Record unchanged green gate certificates so failed validation can resume from the active wound.",
        },
        {
            "candidate_id": "current-pressure-focus",
            "summary": f"Watch {top.get('step', 'no gate')} next; current level is {top.get('pressure_level', 'low')}.",
        },
    ]


def build_predictive_evolve_plan(root: str | Path, max_runs: int = 12) -> dict[str, Any]:
    timing = build_predictive_timing_packet(root, max_runs=max_runs)
    plan = _plan_steps(timing)
    has_high_pressure = any(item.get("pressure_level") == "high" for item in timing.get("runtime_pressure", []))
    status = "warn" if has_high_pressure else "pass"
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "predictive_evolve_dry_run",
        "status": status,
        "generated_utc": _utc(),
        "dry_run": True,
        "read_surfaces": [
            "reports/human_surface/*",
            "git status --porcelain",
            "reports/nexus_predictive_gate_timing_latest.json",
        ],
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            STATE_LATEST.as_posix(),
        ],
        "timing_status": timing.get("status"),
        "runtime_pressure": timing.get("runtime_pressure", []),
        "git_scope": timing.get("git_scope", {}),
        "adaptive_timeout_policy": timing.get("adaptive_timeout_policy", {}),
        "gate_selection_policy": timing.get("gate_selection_policy", {}),
        "recommended_plan": plan,
        "final_evolve_required_before_commit": True,
        "next_evolution_candidates": _next_evolution_candidates(timing),
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "repo_mutation": False,
            "git_write": False,
            "execute_plan": False,
            "skip_final_evolve": False,
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
            "dry_run": packet["dry_run"],
            "git_scope": packet["git_scope"],
            "gate_selection_policy": packet["gate_selection_policy"],
            "recommended_plan": packet["recommended_plan"],
            "final_evolve_required_before_commit": packet["final_evolve_required_before_commit"],
            "blocked_actions": packet["blocked_actions"],
            "claim_boundary": packet["claim_boundary"],
        },
    )


def render(packet: dict[str, Any]) -> str:
    plan = packet.get("recommended_plan", [])
    lines = [
        "NEXUS PREDICTIVE EVOLVE DRY-RUN PLAN",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Scope: {packet.get('git_scope', {}).get('scope', 'unknown')}",
        "Plan:",
    ]
    for step in plan:
        marker = "FINAL" if step.get("required_before_commit") else "NEXT"
        lines.append(f"  {step.get('order')}. [{marker}] {step.get('command')}")
    lines.append("Boundary: recommendation-only; full evolve remains required before commit.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS predictive evolve dry-run plan.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-runs", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    packet = build_predictive_evolve_plan(args.root, max_runs=args.max_runs)
    write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
