from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from nexus_gate.nexus_cell.context_bridge import build_context_bridge
from nexus_gate.nexus_cell.plan import build_plan

VERSION = "0.8.6"

NEXUS_SHELL_COMMANDS = [
    "status",
    "rehydrate",
    "compile",
    "doctor",
    "cell-plan",
    "cell-context",
    "cell-bridge",
    "cell-run",
    "handoff",
    "help",
]

LANE_COMMANDS = {
    "status": ".\\scripts\\nexus.ps1 status",
    "rehydrate": ".\\scripts\\nexus.ps1 rehydrate",
    "compile": ".\\scripts\\nexus.ps1 compile",
    "doctor": "Open Desktop Portal -> Failure Modes / Doctor",
    "cell-plan": ".\\scripts\\nexus.ps1 cell-plan -Tag \"...\"",
    "cell-context": ".\\scripts\\nexus.ps1 cell-context -Tag \"...\"",
    "cell-bridge": ".\\scripts\\nexus.ps1 cell-bridge -Tag \"...\"",
    "cell-run": ".\\scripts\\nexus.ps1 cell-run -Tag \"cell-bridge\"",
    "handoff": "python -m nexus_gate.nexus_shell.shell --command handoff --intent \"...\" --json",
    "help": "python -m nexus_gate.nexus_shell.shell --command help --json",
}

ORGANS = {
    "nexus_gate_root": "README.md",
    "compiler": "nexus_gate/compiler/compiler.py",
    "nexus_cell": "nexus_gate/nexus_cell/context_bridge.py",
    "nexus_shell": "nexus_gate/nexus_shell/shell.py",
    "failure_doctor": "docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md",
    "failure_chart": "docs/failure_modes/FAILURE_MODE_CHART.md",
    "desktop_portal": "scripts/desktop/open_nexus_gate_console.ps1",
    "compact_shell": "scripts/nexus.ps1",
}


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _organ_status(root: Path) -> Dict[str, object]:
    organs = {}
    for name, rel in ORGANS.items():
        path = root / rel
        organs[name] = {
            "path": rel,
            "exists": path.exists(),
            "kind": "file" if path.is_file() else "missing",
        }
    return organs


def _recommended_next(command: str, authority_decision: str) -> List[str]:
    if command == "doctor":
        return ["read failure mode chart", "classify wound", "request human-authorized close script"]
    if command in {"cell-plan", "cell-context", "handoff"}:
        return ["review planner decision", "review context refs", "do not execute without future authority gate"]
    if authority_decision in {"deny", "reject"}:
        return ["do not execute", "revise intent", "review Doctor boundary"]
    if authority_decision in {"shadow", "review"}:
        return ["request human decision", "use context bridge", "block durable mutation"]
    return ["read status", "build context bridge if model handoff is needed", "compile before promotion"]


def build_shell_packet(root: Path, intent: str, command: str = "status", context_limit: int = 10) -> Dict[str, object]:
    if command not in NEXUS_SHELL_COMMANDS:
        command = "help"

    plan = build_plan(root=root, intent=intent)
    context_packet = build_context_bridge(root=root, intent=intent, limit=context_limit)

    organs = _organ_status(root)
    missing_organs = [name for name, data in organs.items() if not data["exists"]]

    packet_seed = json.dumps(
        {
            "command": command,
            "intent_hash": plan.get("intent_hash"),
            "context_bridge_hash": context_packet.get("context_bridge_hash"),
            "missing_organs": missing_organs,
        },
        sort_keys=True,
    )

    return {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "nexus_shell_operator_no_execution",
        "command": command,
        "intent": intent,
        "intent_hash": plan.get("intent_hash"),
        "shell_hash": _sha256_text(packet_seed),
        "lane_command": LANE_COMMANDS.get(command),
        "available_commands": NEXUS_SHELL_COMMANDS,
        "organs": organs,
        "missing_organs": missing_organs,
        "planner": {
            "mode": plan.get("mode"),
            "risk_score": plan.get("risk_score"),
            "authority_decision": plan.get("authority_decision"),
            "route_mode": plan.get("route_mode"),
            "gate_flags": plan.get("gate_flags"),
        },
        "context_bridge": {
            "mode": context_packet.get("mode"),
            "context_bridge_hash": context_packet.get("context_bridge_hash"),
            "context_ref_count": context_packet.get("context_ref_count"),
            "context_refs": context_packet.get("context_refs"),
        },
        "recommended_next": _recommended_next(command, str(plan.get("authority_decision"))),
        "boundary": {
            "execution_enabled": False,
            "backend_enabled": False,
            "network_enabled": False,
            "secrets_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
            "shell_mutation_enabled": False,
        },
        "outputs": {
            "report": "reports/nexus_shell_packet_latest.json",
            "state": "state/nexus_shell/shell_state_latest.json",
        },
        "claim_boundary": "NexusShell routes and summarizes governed operator lanes only; it does not execute arbitrary commands, enable backends, expose secrets, use network, mutate git, claim rollback, or self-authorize.",
    }


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, packet: Dict[str, object]) -> None:
    _write_json(root / "reports" / "nexus_shell_packet_latest.json", packet)
    _write_json(root / "state" / "nexus_shell" / "shell_state_latest.json", {
        "version": VERSION,
        "generated_utc": packet.get("generated_utc"),
        "mode": packet.get("mode"),
        "command": packet.get("command"),
        "intent_hash": packet.get("intent_hash"),
        "shell_hash": packet.get("shell_hash"),
        "authority_decision": packet.get("planner", {}).get("authority_decision"),
        "context_bridge_hash": packet.get("context_bridge", {}).get("context_bridge_hash"),
        "claim_boundary": packet.get("claim_boundary"),
    })


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NexusShell full-scope no-execution operator shell.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="Inspect NexusGate status.", help="Operator intent.")
    parser.add_argument("--command", default="status", choices=NEXUS_SHELL_COMMANDS, help="NexusShell command lane.")
    parser.add_argument("--context-limit", type=int, default=10, help="Maximum context refs.")
    parser.add_argument("--json", action="store_true", help="Print full JSON packet.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state files.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = build_shell_packet(root=root, intent=args.intent, command=args.command, context_limit=args.context_limit)
    if not args.no_write:
        write_outputs(root, packet)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "mode": packet["mode"],
            "command": packet["command"],
            "authority_decision": packet["planner"]["authority_decision"],
            "context_ref_count": packet["context_bridge"]["context_ref_count"],
            "missing_organs": packet["missing_organs"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
