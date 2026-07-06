from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from nexus_gate.nexus_cell.context_bridge import build_context_bridge
from nexus_gate.nexus_cell.core import VERSION, build_cell_contract

BRIDGE_MODE = "nexus_cell_core_bridge_no_execution"

BRIDGE_TARGETS = [
    "nexus_shell_operator",
    "nexus_cell_planner",
    "nexus_cell_context_bridge",
    "failure_doctor",
    "compiler",
]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_cell_bridge_packet(root: Path, intent: str, target: str = "nexus_shell_operator", context_limit: int = 12) -> Dict[str, object]:
    if target not in BRIDGE_TARGETS:
        target = "nexus_shell_operator"

    contract = build_cell_contract(root=root, intent=intent, context_limit=context_limit)
    context_packet = build_context_bridge(root=root, intent=intent, limit=context_limit)

    seed = json.dumps(
        {
            "contract_id": contract.get("cell_contract_id"),
            "target": target,
            "context_bridge_hash": context_packet.get("context_bridge_hash"),
            "cell_phase": contract.get("cell_phase"),
        },
        sort_keys=True,
    )

    packet = {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": BRIDGE_MODE,
        "target": target,
        "intent": intent,
        "bridge_packet_id": _sha256_text(seed),
        "cell_contract": contract,
        "context_refs": context_packet.get("context_refs", []),
        "context_bridge_hash": context_packet.get("context_bridge_hash"),
        "handoff": {
            "allowed": True,
            "kind": "read_only_governance_handoff",
            "target": target,
            "requires_human_authorization_for_mutation": contract.get("human_authorization_required", False),
            "blocked_operations": contract.get("blocked_operations", []),
            "required_authority": contract.get("required_authority", []),
        },
        "outputs": {
            "report": "reports/nexus_cell_bridge_packet_latest.json",
            "state": "state/nexus_cell/bridge_state_latest.json",
        },
        "boundary": {
            "execution_enabled": False,
            "backend_enabled": False,
            "network_enabled": False,
            "secrets_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
            "process_spawn_enabled": False,
            "host_mount_enabled": False,
        },
        "claim_boundary": "NexusCell bridge packet is a read-only governance handoff; it does not run commands, create containers, mount host paths, expose secrets, use network, mutate git, claim rollback, or self-authorize.",
    }
    return packet


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, packet: Dict[str, object]) -> None:
    _write_json(root / "reports" / "nexus_cell_bridge_packet_latest.json", packet)
    _write_json(root / "state" / "nexus_cell" / "bridge_state_latest.json", {
        "version": VERSION,
        "generated_utc": packet.get("generated_utc"),
        "mode": packet.get("mode"),
        "bridge_packet_id": packet.get("bridge_packet_id"),
        "target": packet.get("target"),
        "cell_contract_id": packet.get("cell_contract", {}).get("cell_contract_id"),
        "cell_phase": packet.get("cell_contract", {}).get("cell_phase"),
        "authority_decision": packet.get("cell_contract", {}).get("planner", {}).get("authority_decision"),
        "human_authorization_required": packet.get("cell_contract", {}).get("human_authorization_required"),
        "claim_boundary": packet.get("claim_boundary"),
    })


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a read-only NexusCell core bridge packet.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="", help="Requested action intent.")
    parser.add_argument("--target", default="nexus_shell_operator", choices=BRIDGE_TARGETS, help="Bridge target.")
    parser.add_argument("--context-limit", type=int, default=12, help="Maximum context refs.")
    parser.add_argument("--json", action="store_true", help="Print full JSON packet.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state files.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = build_cell_bridge_packet(root=root, intent=args.intent, target=args.target, context_limit=args.context_limit)
    if not args.no_write:
        write_outputs(root, packet)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "mode": packet["mode"],
            "target": packet["target"],
            "cell_phase": packet["cell_contract"]["cell_phase"],
            "authority_decision": packet["cell_contract"]["planner"]["authority_decision"],
            "human_authorization_required": packet["cell_contract"]["human_authorization_required"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
