from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.loops.meta_orchestrator_gate import build_meta_orchestrator_packet
from nexus_gate.loops.registry import list_loops
from nexus_gate.loops.runner import build_loop_packet, write_outputs as write_loop_outputs


VERSION = "1.1.4"
SCHEMA = "NEXUS_LOOP_ORCHESTRATOR.v1.1.4"
REPORT_LATEST = Path("reports") / "nexus_loop_orchestration_report_latest.json"
STATE_LATEST = Path("state") / "loops" / "nexus_loop_orchestration_latest.json"

CLAIM_BOUNDARY = (
    "Loop orchestration is local development evidence only. It may select and "
    "run allowlisted non-mutating loop stages when human-authorized; it does "
    "not grant autonomous authority, arbitrary shell execution, git write, "
    "secret access, external API writes, or repo mutation from model output."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "arbitrary_shell_commands",
    "autonomous_repo_mutation",
    "git_write",
    "secret_access",
    "external_api_writes",
    "model_output_tool_execution",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _select_loop(recommended: str, available: list[str]) -> tuple[str, str]:
    if recommended in available:
        return recommended, "meta_orchestrator_recommendation"
    aliases = {
        "evolution-radar": "evolution-radar",
        "scope-hygiene": "scope-hygiene",
        "compiler-wound-focus": "compiler-wound-focus",
        "wound-indexed-resume": "wound-indexed-resume",
        "phi-gate-seal": "compiler-wound-focus",
    }
    alias = aliases.get(recommended)
    if alias in available:
        return alias, f"alias_for:{recommended}"
    fallback = "toolbelt-next" if "toolbelt-next" in available else "rhp-core"
    return fallback, f"fallback_for:{recommended or 'none'}"


def build_orchestration_packet(
    root: str | Path,
    intent: str = "",
    execute: bool = False,
    human_authorized: bool = False,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    available = list_loops(root_path)
    meta = build_meta_orchestrator_packet(root_path, intent)
    recommended = str(meta.get("recommended_next_loop") or "")
    selected_loop, selection_reason = _select_loop(recommended, available)
    selected_plan = build_loop_packet(
        root=root_path,
        loop_name=selected_loop,
        intent=intent,
        execute=bool(execute),
        human_authorized=bool(human_authorized),
        timeout_seconds=timeout_seconds,
    )

    mutating_requested = bool(execute and selected_plan.get("mutates"))
    status = selected_plan.get("status", "unknown")
    if mutating_requested:
        status = "blocked"

    packet = {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "loop_orchestrator",
        "status": status,
        "generated_utc": _utc(),
        "intent": intent,
        "execute_requested": bool(execute),
        "human_authorized": bool(human_authorized),
        "meta_recommendation": {
            "status": meta.get("status"),
            "recommended_next_loop": recommended,
            "recommended_next_command": meta.get("recommended_next_command"),
            "why": meta.get("why"),
        },
        "selected_loop": selected_loop,
        "selection_reason": selection_reason,
        "selected_loop_packet_id": selected_plan.get("loop_packet_id"),
        "selected_loop_status": selected_plan.get("status"),
        "available_loop_count": len(available),
        "available_loops": available,
        "loop_packet": selected_plan,
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            STATE_LATEST.as_posix(),
            "reports/nexus_loop_packet_latest.json",
            "state/loops/loop_state_latest.json",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "human_authorized_execution_only": True,
            "mutating_loop_execution": False,
            "arbitrary_shell_execution": False,
            "autonomous_authority": False,
            "ui_authority": False,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if mutating_requested:
        packet["blocker"] = "Selected loop is marked mutating; orchestrator will not execute mutating loops."
    return packet


def write_outputs(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    _write_json(root_path / REPORT_LATEST, packet)
    _write_json(root_path / STATE_LATEST, {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "generated_utc": packet["generated_utc"],
        "selected_loop": packet["selected_loop"],
        "selection_reason": packet["selection_reason"],
        "selected_loop_packet_id": packet["selected_loop_packet_id"],
        "execute_requested": packet["execute_requested"],
        "human_authorized": packet["human_authorized"],
        "blocked_actions": packet["blocked_actions"],
        "claim_boundary": packet["claim_boundary"],
    })
    write_loop_outputs(root_path, packet["loop_packet"])


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS LOOP ORCHESTRATOR",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Selected loop: {packet.get('selected_loop')}",
        f"Selection: {packet.get('selection_reason')}",
        f"Meta why: {packet.get('meta_recommendation', {}).get('why')}",
        "Boundary: recommendation-only; non-mutating loop execution requires explicit human authorization.",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile or run the bounded NEXUS loop orchestrator.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Orchestrate the next NEXUS loop.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--human-authorized", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    packet = build_orchestration_packet(
        root=args.root,
        intent=args.intent,
        execute=args.execute,
        human_authorized=args.human_authorized,
        timeout_seconds=args.timeout_seconds,
    )
    write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn", "planned", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
