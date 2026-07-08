from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

from nexus_gate.loops.registry import LoopRegistryError, file_digest, get_loop, list_loops, load_registry


RUNNER_MODE = "nexus_meta_loop_runner"


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_preview(path: Path, max_lines: int) -> List[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return lines[: max(0, int(max_lines))]


def _resolve_command(loop: Dict[str, Any], command_name: str) -> Dict[str, Any]:
    allowed = loop.get("_allowed_commands", {})
    command = allowed.get(command_name)
    if not isinstance(command, dict):
        raise LoopRegistryError(f"Stage references unknown command {command_name!r}.")
    argv = command.get("argv")
    if not isinstance(argv, list) or not argv:
        raise LoopRegistryError(f"Command {command_name!r} has invalid argv.")
    if any(not isinstance(part, str) for part in argv):
        raise LoopRegistryError(f"Command {command_name!r} argv must be a list of strings.")
    return command


def _run_command(root: Path, argv: List[str], timeout_seconds: int) -> Dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=str(root),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "executed": True,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def _stage_read(root: Path, stage: Dict[str, Any]) -> Dict[str, Any]:
    rel = Path(str(stage["path"]))
    path = root / rel
    required = bool(stage.get("required", True))
    max_preview_lines = int(stage.get("max_preview_lines", 25))
    digest = file_digest(path)
    status = "pass"
    if required and not digest["exists"]:
        status = "fail"
    if not required and not digest["exists"]:
        status = "skip"
    return {
        "name": stage["name"],
        "type": "read",
        "status": status,
        "path": str(rel).replace("\\", "/"),
        "required": required,
        "digest": digest,
        "preview": _read_preview(path, max_preview_lines),
    }


def _stage_command(
    root: Path,
    loop: Dict[str, Any],
    stage: Dict[str, Any],
    execute: bool,
    human_authorized: bool,
    timeout_seconds: int,
) -> Dict[str, Any]:
    command_name = str(stage["command"])
    command = _resolve_command(loop, command_name)
    argv = list(command["argv"])
    mutates = bool(command.get("mutates", False))
    result: Dict[str, Any] = {
        "name": stage["name"],
        "type": "command",
        "status": "planned",
        "command": command_name,
        "argv": argv,
        "mutates": mutates,
        "description": command.get("description", ""),
        "execution": {
            "executed": False,
            "exit_code": None,
            "stdout_tail": "",
            "stderr_tail": "",
            "reason": "no_execute_requested",
        },
    }
    if not execute:
        return result
    if not human_authorized:
        result["status"] = "blocked"
        result["execution"]["reason"] = "human_authorization_required"
        return result
    if mutates:
        result["status"] = "blocked"
        result["execution"]["reason"] = "mutating_commands_blocked_by_meta_loop_v0_1"
        return result

    execution = _run_command(root=root, argv=argv, timeout_seconds=timeout_seconds)
    result["execution"] = {
        **execution,
        "reason": "allowlisted_command_executed",
    }
    result["status"] = "pass" if execution["exit_code"] == 0 else "fail"
    return result


def _execute_loop(
    root: Path,
    loop_name: str,
    intent: str,
    execute: bool,
    human_authorized: bool,
    timeout_seconds: int,
    depth: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    if depth > 4:
        raise LoopRegistryError("Loop nesting depth exceeded.")
    loop = get_loop(root, loop_name)
    stages_out: List[Dict[str, Any]] = []
    exit_code = 0
    stop_on_failure = bool(loop.get("stop_on_failure", True))

    for stage in loop.get("stages", []):
        stage_type = stage.get("type")
        if stage_type == "read":
            result = _stage_read(root, stage)
        elif stage_type == "command":
            result = _stage_command(
                root=root,
                loop=loop,
                stage=stage,
                execute=execute,
                human_authorized=human_authorized,
                timeout_seconds=timeout_seconds,
            )
        elif stage_type == "loop_ref":
            ref = str(stage["loop"])
            nested_stages, nested_exit = _execute_loop(
                root=root,
                loop_name=ref,
                intent=intent,
                execute=execute,
                human_authorized=human_authorized,
                timeout_seconds=timeout_seconds,
                depth=depth + 1,
            )
            result = {
                "name": stage["name"],
                "type": "loop_ref",
                "status": "pass" if nested_exit == 0 else "fail",
                "loop": ref,
                "stages": nested_stages,
            }
        else:
            result = {
                "name": stage.get("name", "unnamed"),
                "type": stage_type,
                "status": "fail",
                "error": f"Unknown stage type: {stage_type}",
            }

        stages_out.append(result)

        if result.get("status") == "fail":
            exit_code = 1
        command_exit = result.get("execution", {}).get("exit_code") if isinstance(result.get("execution"), dict) else None
        if isinstance(command_exit, int) and command_exit != 0:
            exit_code = command_exit
        if stop_on_failure and result.get("status") == "fail":
            break

    return stages_out, int(exit_code)


def build_loop_packet(
    root: str | Path,
    loop_name: str,
    intent: str = "",
    execute: bool = False,
    human_authorized: bool = False,
    timeout_seconds: int = 180,
) -> Dict[str, Any]:
    root_path = Path(root).resolve()
    registry = load_registry(root_path)
    loop = get_loop(root_path, loop_name)
    stages, exit_code = _execute_loop(
        root=root_path,
        loop_name=loop_name,
        intent=intent,
        execute=execute,
        human_authorized=human_authorized,
        timeout_seconds=timeout_seconds,
    )
    seed = json.dumps(
        {
            "loop": loop_name,
            "intent": intent,
            "execute": execute,
            "human_authorized": human_authorized,
            "stages": stages,
            "registry_hash": loop.get("_registry_hash"),
        },
        sort_keys=True,
        default=str,
    )
    status = "pass" if exit_code == 0 else "fail"
    if any(stage.get("status") == "blocked" for stage in stages):
        status = "blocked"
    packet = {
        "version": registry.get("version"),
        "generated_utc": _utc_now(),
        "mode": RUNNER_MODE,
        "loop": loop_name,
        "intent": intent,
        "intent_hash": _sha256_text(intent or ""),
        "loop_packet_id": _sha256_text(seed),
        "status": status,
        "exit_code": exit_code,
        "execute_requested": bool(execute),
        "human_authorized": bool(human_authorized),
        "registry_path": loop.get("_registry_path"),
        "registry_hash": loop.get("_registry_hash"),
        "available_loops": sorted(registry.get("loops", {}).keys()),
        "description": loop.get("description", ""),
        "mutates": bool(loop.get("mutates", False)),
        "requires_human_authorization": bool(loop.get("requires_human_authorization", False)),
        "authority_boundary": loop.get("_authority_boundary", {}),
        "stages": stages,
        "outputs": {
            "report": "reports/nexus_loop_packet_latest.json",
            "state": "state/loops/loop_state_latest.json",
        },
        "claim_boundary": loop.get("_claim_boundary", registry.get("claim_boundary", "")),
    }
    return packet


def write_outputs(root: str | Path, packet: Dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    report = root_path / "reports" / "nexus_loop_packet_latest.json"
    state = root_path / "state" / "loops" / "loop_state_latest.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    state.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    state.write_text(
        json.dumps(
            {
                "version": packet.get("version"),
                "generated_utc": packet.get("generated_utc"),
                "mode": packet.get("mode"),
                "loop": packet.get("loop"),
                "status": packet.get("status"),
                "exit_code": packet.get("exit_code"),
                "loop_packet_id": packet.get("loop_packet_id"),
                "registry_hash": packet.get("registry_hash"),
                "claim_boundary": packet.get("claim_boundary"),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nexus meta loop runner.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--loop", default="rhp-core", help="Named loop.")
    parser.add_argument("--intent", default="", help="Human intent for this loop trigger.")
    parser.add_argument("--execute", action="store_true", help="Execute allowlisted command stages.")
    parser.add_argument("--human-authorized", action="store_true", help="Human explicitly authorizes command execution.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Per-command timeout.")
    parser.add_argument("--json", action="store_true", help="Print full JSON packet.")
    parser.add_argument("--list", action="store_true", help="List available loops.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state outputs.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()

    if args.list:
        data = {
            "ok": True,
            "mode": RUNNER_MODE,
            "available_loops": list_loops(root),
            "registry_path": load_registry(root).get("_registry_path"),
        }
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0

    packet = build_loop_packet(
        root=root,
        loop_name=args.loop,
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
            "ok": packet["status"] in {"pass", "blocked"},
            "mode": packet["mode"],
            "loop": packet["loop"],
            "status": packet["status"],
            "exit_code": packet["exit_code"],
            "loop_packet_id": packet["loop_packet_id"],
        }, indent=2, sort_keys=True))
    return int(packet["exit_code"] or 0)


if __name__ == "__main__":
    raise SystemExit(main())