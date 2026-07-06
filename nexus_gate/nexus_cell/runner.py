from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict, List

from nexus_gate.nexus_cell.authority import evaluate_authority
from nexus_gate.nexus_cell.bridge import build_cell_bridge_packet
from nexus_gate.nexus_cell.policy import CONTROLLED_LANES, VERSION, capability_policy, lane_policy, list_lanes
from nexus_gate.nexus_cell.receipt import build_receipt

RUNNER_MODE = "nexus_cell_full_core_controlled_runner"


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _lane_argv(lane: str, root: Path, intent: str) -> List[str]:
    base = list(CONTROLLED_LANES[lane]["argv"])
    updated: List[str] = []
    i = 0
    while i < len(base):
        value = base[i]
        if value == ".":
            updated.append(str(root))
        elif value == "NexusCell controlled planner lane":
            updated.append(intent)
        elif value == "NexusCell controlled context lane":
            updated.append(intent)
        elif value == "NexusCell controlled bridge lane":
            updated.append(intent)
        elif value == "NexusCell controlled status lane":
            updated.append(intent)
        else:
            updated.append(value)
        i += 1
    return updated


def build_run_packet(
    root: Path,
    lane: str,
    intent: str = "",
    execute: bool = False,
    human_authorized: bool = False,
    timeout_seconds: int = 120,
) -> Dict[str, object]:
    if lane not in CONTROLLED_LANES:
        lane = "cell-bridge"

    bridge = build_cell_bridge_packet(root=root, intent=intent or f"NexusCell lane: {lane}", target="nexus_shell_operator", context_limit=10)
    cap_policy = capability_policy(bridge.get("cell_contract", {}).get("planner", {}).get("capability_vector", {}))
    lane_meta = lane_policy(lane)
    authority = evaluate_authority(
        lane_policy=lane_meta,
        capability_policy=cap_policy,
        human_authorized=human_authorized,
        execute_requested=execute,
    )

    argv = _lane_argv(lane, root, intent or f"NexusCell lane: {lane}")
    execution = {
        "executed": False,
        "exit_code": None,
        "stdout_tail": "",
        "stderr_tail": "",
        "reason": "no_execute_requested" if not execute else "authority_denied",
    }

    if execute and authority["may_execute_controlled_lane"]:
        completed = subprocess.run(
            argv,
            cwd=str(root),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        execution = {
            "executed": True,
            "exit_code": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
            "reason": "controlled_lane_executed",
        }

    seed = json.dumps(
        {
            "lane": lane,
            "intent_hash": bridge.get("cell_contract", {}).get("intent_hash"),
            "authority": authority,
            "argv": argv,
            "execution": execution,
        },
        sort_keys=True,
    )

    packet = {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": RUNNER_MODE,
        "lane": lane,
        "intent": intent,
        "intent_hash": bridge.get("cell_contract", {}).get("intent_hash"),
        "run_packet_id": _sha256_text(seed),
        "available_lanes": list_lanes(),
        "argv": argv,
        "lane_policy": lane_meta,
        "capability_policy": cap_policy,
        "authority": authority,
        "execute_requested": execute,
        "human_authorized": human_authorized,
        "cell_contract": bridge.get("cell_contract"),
        "bridge_packet_id": bridge.get("bridge_packet_id"),
        "execution": execution,
        "boundary": {
            "arbitrary_command_execution": False,
            "controlled_lane_execution_requested": bool(execute),
            "controlled_lane_executed": bool(execution["executed"]),
            "network_enabled": False,
            "secrets_enabled": False,
            "host_mount_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
            "self_authorization_enabled": False,
        },
        "outputs": {
            "report": "reports/nexus_cell_run_packet_latest.json",
            "state": "state/nexus_cell/run_state_latest.json",
        },
        "claim_boundary": "NexusCell full core runs only named controlled internal lanes when explicitly human-authorized; it does not provide arbitrary shell execution, sandbox proof, host mounts, secrets, network, git mutation, rollback, or autonomous authority.",
    }
    packet["receipt"] = build_receipt(packet)
    return packet


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, packet: Dict[str, object]) -> None:
    _write_json(root / "reports" / "nexus_cell_run_packet_latest.json", packet)
    _write_json(root / "state" / "nexus_cell" / "run_state_latest.json", {
        "version": VERSION,
        "generated_utc": packet.get("generated_utc"),
        "mode": packet.get("mode"),
        "lane": packet.get("lane"),
        "run_packet_id": packet.get("run_packet_id"),
        "receipt_id": packet.get("receipt", {}).get("receipt_id"),
        "authority": packet.get("authority"),
        "execution": packet.get("execution"),
        "claim_boundary": packet.get("claim_boundary"),
    })


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NexusCell full core controlled runner.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--lane", default="cell-bridge", choices=list_lanes(), help="Controlled lane.")
    parser.add_argument("--intent", default="", help="Intent.")
    parser.add_argument("--execute", action="store_true", help="Execute controlled lane if authority permits.")
    parser.add_argument("--human-authorized", action="store_true", help="Human explicitly authorizes controlled lane execution.")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Controlled lane timeout.")
    parser.add_argument("--json", action="store_true", help="Print full JSON.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = build_run_packet(
        root=root,
        lane=args.lane,
        intent=args.intent,
        execute=args.execute,
        human_authorized=args.human_authorized,
        timeout_seconds=args.timeout_seconds,
    )
    if not args.no_write:
        write_outputs(root, packet)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "mode": packet["mode"],
            "lane": packet["lane"],
            "decision": packet["authority"]["decision"],
            "executed": packet["execution"]["executed"],
            "receipt_id": packet["receipt"]["receipt_id"],
        }, indent=2, sort_keys=True))
    return int(packet["execution"]["exit_code"] or 0) if packet["execution"]["executed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
