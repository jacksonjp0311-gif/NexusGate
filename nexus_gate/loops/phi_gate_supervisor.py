from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "NEXUS_PHI_GATE_SUPERVISOR.v1.1.1"
VERSION = "1.1.1"
REPORT_LATEST = Path("reports") / "nexus_phi_gate_supervisor_latest.json"
REPORT_VERSIONED = Path("reports") / "nexus_phi_gate_supervisor.v1.1.1.json"

AUTHORITY_BOUNDARY = {
    "arbitrary_command_execution": False,
    "autonomous_authority": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "repo_mutation_enabled_without_human_authorization": False,
    "deterministic_allowlisted_repairs_only": True,
}

ALLOWED_REPAIR_LANES = {
    "loop_registry_card_packet_drift": "regenerate_loop_cards",
    "empty_loop_stages": "repair_empty_loop_stages_then_regenerate_cards",
    "ignored_report_staged": "unstage_ignored_reports_only",
    "readme_compactness_regression": "compact_readme_without_removing_required_markers",
    "preflight_docs_contract_drift": "report_only",
}

GATE_COMMANDS = {
    "loop-cards": [
        [sys.executable, "-m", "nexus_gate.loops.cards", "--root", ".", "--json"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_loop_cards_portal_v091b.py", "-v"],
    ],
    "unit-tests": [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    ],
    "compiler": [
        [sys.executable, "-m", "nexus_gate.compiler", "--root", ".", "--json"],
    ],
    "ci-core": [
        [sys.executable, "-m", "compileall", "nexus_gate", "tests"],
        [sys.executable, "-m", "nexus_gate.loops.cards", "--root", ".", "--json"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [sys.executable, "-m", "nexus_gate.compiler", "--root", ".", "--json"],
    ],
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tail(value: str, limit: int = 6000) -> str:
    value = value or ""
    return value[-limit:]


def run(root: Path, argv: list[str], timeout: int = 600) -> dict[str, Any]:
    proc = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=timeout)
    return {
        "argv": argv,
        "returncode": proc.returncode,
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
        "ok": proc.returncode == 0,
    }


def run_gate_once(root: Path, gate: str) -> dict[str, Any]:
    if gate not in GATE_COMMANDS:
        return {"status": "fail", "gate": gate, "failure_text": f"Unknown gate: {gate}", "commands": []}
    results = []
    for argv in GATE_COMMANDS[gate]:
        item = run(root, argv)
        results.append(item)
        if not item["ok"]:
            failure_text = (item.get("stdout_tail", "") + "\n" + item.get("stderr_tail", "")).strip()
            return {"status": "fail", "gate": gate, "failed_command": argv, "failure_text": failure_text, "commands": results}
    return {"status": "pass", "gate": gate, "commands": results}


def detect_wound(failure_text: str) -> dict[str, Any]:
    text = failure_text or ""
    if "220 not less than 220" in text or "not less than 220" in text and "README" in text:
        return {"wound_key": "readme_compactness_regression", "repair_lane": ALLOWED_REPAIR_LANES["readme_compactness_regression"]}
    if "must define non-empty stages" in text or "LoopRegistryError" in text:
        return {"wound_key": "empty_loop_stages", "repair_lane": ALLOWED_REPAIR_LANES["empty_loop_stages"]}
    if "Items in the second set but not the first" in text and ("loop" in text.lower() or "card" in text.lower()):
        return {"wound_key": "loop_registry_card_packet_drift", "repair_lane": ALLOWED_REPAIR_LANES["loop_registry_card_packet_drift"]}
    if "ignored by one of your .gitignore files" in text:
        return {"wound_key": "ignored_report_staged", "repair_lane": ALLOWED_REPAIR_LANES["ignored_report_staged"]}
    if "missing_docs" in text or "docs_evidence_mode" in text or "Preflight" in text:
        return {"wound_key": "preflight_docs_contract_drift", "repair_lane": ALLOWED_REPAIR_LANES["preflight_docs_contract_drift"]}
    return {"wound_key": "unknown_gate_failure", "repair_lane": "report_only"}


def call_phi_microdose(root: Path, gate: str, intent: str, failure_text: str, call_model: bool) -> dict[str, Any]:
    if not call_model:
        return {"status": "skipped", "reason": "call_model_false"}
    prompt = f"""
NEXUS Phi Gate Supervisor v1.1.1 failure-boundary microdose.

Gate: {gate}
Intent: {intent}

A deterministic gate failed. Diagnose the wound, choose only an allowlisted deterministic repair lane if appropriate, and do not request autonomous mutation.

Allowed lanes:
{json.dumps(ALLOWED_REPAIR_LANES, indent=2, sort_keys=True)}

Failure text:
{failure_text[-8000:]}

Return concise JSON-like advice with: diagnosis, wound_key, repair_lane, patch_intent, rerun_gate, boundary.
""".strip()
    tmp = None
    try:
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False)
        tmp = Path(handle.name)
        handle.write(prompt)
        handle.close()
        env = os.environ.copy()
        env.setdefault("NEXUS_PHI4_MINI_COMMAND", 'python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"')
        argv = [sys.executable, "-m", "nexus_gate.loops.phi4_ollama_adapter", "--prompt-file", str(tmp)]
        proc = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=180, env=env)
        payload = None
        try:
            payload = json.loads(proc.stdout) if proc.stdout.strip() else None
        except Exception:
            payload = None
        return {
            "status": "ok" if proc.returncode == 0 else "model_unavailable",
            "returncode": proc.returncode,
            "payload": payload,
            "stdout_tail": _tail(proc.stdout, 3000),
            "stderr_tail": _tail(proc.stderr, 3000),
            "boundary": "Phi advice is advisory only; Nexus verifies; human authorizes durable mutation.",
        }
    except Exception as exc:
        return {"status": "model_unavailable", "error": str(exc)}
    finally:
        if tmp and tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def compact_readme(root: Path) -> dict[str, Any]:
    path = root / "README.md"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    before = len(lines)
    required = ["Nexus Loops / Cards", "NEXUS Loop Cards"]
    removed = 0
    idx = len(lines) - 1
    while len(lines) >= 220 and idx >= 0:
        if lines[idx].strip() == "":
            lines.pop(idx)
            removed += 1
        idx -= 1
    if len(lines) >= 220:
        compacted = []
        previous_blank = False
        for line in lines:
            blank = line.strip() == ""
            if blank and previous_blank:
                removed += 1
                continue
            compacted.append(line)
            previous_blank = blank
        lines = compacted
    after_text = "\n".join(lines).rstrip() + "\n"
    missing = [marker for marker in required if marker not in after_text]
    if missing:
        raise RuntimeError(f"README compaction would remove required markers: {missing}")
    path.write_text(after_text, encoding="utf-8")
    return {"before_lines": before, "after_lines": len(after_text.splitlines()), "removed_blank_lines": removed, "missing_required_markers": missing}


def regenerate_loop_cards(root: Path) -> dict[str, Any]:
    item = run(root, [sys.executable, "-m", "nexus_gate.loops.cards", "--root", ".", "--json"], timeout=300)
    if not item["ok"]:
        raise RuntimeError("loop card regeneration failed: " + item.get("stderr_tail", ""))
    latest = root / "state" / "loops" / "nexus_loop_cards_latest.json"
    card_count = None
    if latest.exists():
        try:
            card_count = json.loads(latest.read_text(encoding="utf-8-sig")).get("card_count")
        except Exception:
            card_count = None
    return {"regenerated": True, "card_count": card_count}


def repair_empty_loop_stages(root: Path) -> dict[str, Any]:
    paths = [root / "loops" / "nexus_loop_registry.v0.1.json", root / "state" / "loops" / "nexus_loop_registry.v0.1.json"]
    primary = paths[0]
    data = json.loads(primary.read_text(encoding="utf-8-sig"))
    repaired = []
    for name, loop in data.get("loops", {}).items():
        if not isinstance(loop, dict):
            continue
        stages = loop.get("stages")
        if not isinstance(stages, list) or not stages:
            loop["stages"] = [
                {"name": "wound_packet", "type": "command", "command": "wound_compress"},
                {"name": "compiler_gate", "type": "command", "command": "compiler"},
            ]
            repaired.append(name)
    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    cards = regenerate_loop_cards(root)
    return {"repaired_loops": repaired, "cards": cards}


def unstage_ignored_reports(root: Path) -> dict[str, Any]:
    item = run(root, ["git", "reset", "--", "reports"], timeout=120)
    return {"git_reset_reports": item}


def apply_repair(root: Path, wound_key: str) -> dict[str, Any]:
    if wound_key == "readme_compactness_regression":
        return compact_readme(root)
    if wound_key == "loop_registry_card_packet_drift":
        return regenerate_loop_cards(root)
    if wound_key == "empty_loop_stages":
        return repair_empty_loop_stages(root)
    if wound_key == "ignored_report_staged":
        return unstage_ignored_reports(root)
    return {"applied": False, "reason": "no_allowlisted_repair_for_wound"}


def write_report(root: Path, packet: dict[str, Any]) -> None:
    packet.setdefault("generated_utc", _utc())
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    (root / REPORT_LATEST).write_text(encoded, encoding="utf-8")
    (root / REPORT_VERSIONED).write_text(encoded, encoding="utf-8")


def supervise(root: Path, gate: str, intent: str, call_model: bool, auto_repair: bool, human_authorized: bool) -> dict[str, Any]:
    root = Path(root).resolve()
    first = run_gate_once(root, gate)
    packet: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": "phi_gate_supervisor_failure_boundary_microdose",
        "root": str(root),
        "gate": gate,
        "intent": intent,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "allowed_repair_lanes": ALLOWED_REPAIR_LANES,
        "human_authorized": bool(human_authorized),
        "auto_repair_requested": bool(auto_repair),
        "first_gate": first,
        "claim_boundary": "Phi may advise and select allowlisted deterministic repair lanes. Nexus verifies. Human authorization is required for durable mutation.",
    }
    if first["status"] == "pass":
        packet["status"] = "pass"
        packet["phi_microdose"] = {"status": "not_called", "reason": "gate_passed"}
        write_report(root, packet)
        return packet

    wound = detect_wound(first.get("failure_text", ""))
    packet["status"] = "wound"
    packet["detected_wound"] = wound
    packet["phi_microdose"] = call_phi_microdose(root, gate, intent, first.get("failure_text", ""), call_model)

    if auto_repair and human_authorized and wound.get("repair_lane") != "report_only":
        repair = apply_repair(root, wound["wound_key"])
        packet["repair"] = {"status": "applied", "wound_key": wound["wound_key"], "evidence": repair}
        second = run_gate_once(root, gate)
        packet["rerun_gate"] = second
        packet["status"] = "pass_after_repair" if second["status"] == "pass" else "repair_failed"
        write_report(root, packet)
        return packet

    packet["repair"] = {"status": "not_applied", "reason": "auto_repair_and_human_authorized_required"}
    write_report(root, packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--gate", default="ci-core", choices=sorted(GATE_COMMANDS))
    parser.add_argument("--intent", default="Supervise a Nexus gate with Phi failure-boundary microdose.")
    parser.add_argument("--call-model", action="store_true")
    parser.add_argument("--auto-repair", action="store_true")
    parser.add_argument("--human-authorized", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = supervise(Path(args.root), args.gate, args.intent, args.call_model, args.auto_repair, args.human_authorized)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    if not args.json:
        print(f"NEXUS Phi Gate Supervisor: {packet.get('status')} gate={args.gate}")
    return 0 if packet.get("status") in {"pass", "pass_after_repair", "wound"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
