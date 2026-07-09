from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.1.0"
SCHEMA = "NEXUS_PHI_MICRODOSE_LOOP.v1.1.0"
MODE = "nexus_phi_microdose_loop"

BOUNDARY = {
    "repo_mutation_enabled": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "secrets_enabled": False,
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
    "patch_apply_enabled": False,
    "allowlisted_readonly_gate_execution": True,
    "localhost_model_call_enabled": True,
}

AUTONOMY_POLICY = {
    "level": "bounded_microdose_v1",
    "grants": [
        "run_allowlisted_readonly_gates",
        "call_local_phi_adapter",
        "write_evidence_packets",
        "choose_next_readonly_gate",
        "emit_patch_plan",
    ],
    "blocked": [
        "repo_file_mutation",
        "git_stage",
        "git_commit",
        "git_push",
        "secret_access",
        "external_network",
        "arbitrary_shell",
        "durable_memory_promotion_without_gate",
        "self_authorized_patch_apply",
    ],
    "human_authorization_required_for": [
        "file_edits",
        "git_stage",
        "git_commit",
        "git_push",
        "deletion",
        "dependency_install",
        "external_api_call",
    ],
}

TRUTH_RULE = {
    "stdout": "smoke_only",
    "file_packets": "truth",
    "tail": "never_truth",
    "model_output": "advisory_only",
    "compiler_report": "reports/nexus_compile_report_latest.json",
    "wound_report": "reports/nexus_wound_compression_latest.json",
    "phi_report": "reports/nexus_phi_wound_advisor_latest.json",
}

ALLOWLISTED_GATE_COMMANDS = {
    "wound_compress": ["python", "-m", "nexus_gate.loops.wound_compression", "--root", ".", "--json"],
    "compiler": ["python", "-m", "nexus_gate.compiler", "--root", ".", "--json"],
    "preflight": ["python", "-m", "nexus_gate.loops.preflight_optimizer", "--root", ".", "--json"],
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run(root: Path, args: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, cwd=str(root), capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-2000:],
        }
    except Exception as exc:
        return {"ok": False, "returncode": -1, "stdout_tail": "", "stderr_tail": str(exc)}


def _git_status(root: Path) -> dict[str, Any]:
    status = _run(root, ["git", "status", "--short"], timeout=20)
    lines = [line for line in status.get("stdout_tail", "").splitlines() if line.strip()]
    head = _run(root, ["git", "rev-parse", "--short", "HEAD"], timeout=20).get("stdout_tail", "").strip()
    return {"head": head, "dirty": bool(lines), "changed_count": len(lines), "status_preview": lines[:50]}


def _ensure_default_phi_adapter_env(root: Path) -> str:
    current = os.environ.get("NEXUS_PHI4_MINI_COMMAND") or os.environ.get("NEXUS_PHI4_MINI_CMD")
    if current:
        return current
    command = 'python -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{prompt_file}"'
    os.environ["NEXUS_PHI4_MINI_COMMAND"] = command
    return command


def _run_known_gates(root: Path, intent: str) -> dict[str, Any]:
    results: dict[str, Any] = {}
    wc = ALLOWLISTED_GATE_COMMANDS["wound_compress"] + ["--intent", intent]
    results["wound_compress"] = _run(root, wc, timeout=120)
    results["compiler"] = _run(root, ALLOWLISTED_GATE_COMMANDS["compiler"], timeout=900)
    return results


def _call_phi_advisor(root: Path, intent: str, call_model: bool) -> dict[str, Any]:
    if not call_model:
        return {"called": False, "packet": {}, "model_status": "not_requested", "advice_source": "not_requested"}
    _ensure_default_phi_adapter_env(root)
    try:
        from nexus_gate.loops.phi_wound_advisor import build_phi_wound_advisor_packet
        packet = build_phi_wound_advisor_packet(root, intent, call_model=True, require_model=False)
        model_status = packet.get("model_channel", {}).get("model_status")
        advice = packet.get("advice", {}) if isinstance(packet.get("advice"), dict) else {}
        advice_source = "model" if model_status == "ok" else advice.get("source", "deterministic_fallback")
        return {"called": True, "packet": packet, "model_status": model_status, "advice_source": advice_source}
    except Exception as exc:
        return {"called": True, "packet": {}, "model_status": "error", "advice_source": "deterministic_fallback", "error": str(exc)}


def _summarize_compiler(compiler: dict[str, Any]) -> dict[str, Any]:
    gates = compiler.get("gates", []) if isinstance(compiler, dict) else []
    failed = []
    if isinstance(gates, list):
        failed = [g.get("gate") for g in gates if isinstance(g, dict) and g.get("status") == "fail"]
    return {
        "status": compiler.get("status") if isinstance(compiler, dict) else None,
        "gate_count": len(gates) if isinstance(gates, list) else None,
        "failed_gates": failed,
    }


def _derive_patch_plan(wound: dict[str, Any], compiler: dict[str, Any], phi: dict[str, Any], git: dict[str, Any]) -> dict[str, Any]:
    active = wound.get("active_wound", {}) if isinstance(wound, dict) else {}
    compiler_summary = _summarize_compiler(compiler)
    failed = compiler_summary.get("failed_gates") or []
    model_packet = phi.get("packet", {}) if isinstance(phi, dict) else {}
    model_advice = model_packet.get("advice", {}) if isinstance(model_packet, dict) else {}
    if failed:
        return {
            "plan_type": "compiler_wound_plan",
            "repair_surface": "compiler_failed_gate_surface",
            "reason": "Compiler has failed gates; patch smallest failed gate surface only.",
            "next_gate": "python -m nexus_gate.compiler --root . --json",
            "failed_gates": failed,
            "model_diagnosis": model_advice.get("diagnosis"),
            "may_apply_without_human": False,
        }
    if active.get("wound_key") == "git:dirty_worktree" or git.get("dirty"):
        return {
            "plan_type": "scope_hygiene_plan",
            "repair_surface": active.get("next_repair_surface") or "scope_hygiene_or_stage_policy",
            "reason": "Dirty worktree is evidence pressure, not a code defect. Compress, inspect, then human chooses stage/revert/keep.",
            "next_gate": ".\\scripts\\nexus.ps1 preflight-json",
            "changed_count": git.get("changed_count"),
            "model_diagnosis": model_advice.get("diagnosis"),
            "may_apply_without_human": False,
        }
    return {
        "plan_type": "green_evolution_plan",
        "repair_surface": "next_bounded_loop_selection",
        "reason": "Compiler is green and no active wound is present. Continue evolution by preflight or toolbelt.",
        "next_gate": ".\\scripts\\nexus.ps1 preflight-json",
        "model_diagnosis": model_advice.get("diagnosis"),
        "may_apply_without_human": False,
    }


def build_phi_microdose_packet(root: str | Path, intent: str = "", run_gates: bool = False, call_model: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    if not intent:
        intent = "Run bounded Phi microdose loop."
    gate_results = _run_known_gates(root, intent) if run_gates else {}
    wound = _read_json(root / "reports" / "nexus_wound_compression_latest.json", {})
    compiler = _read_json(root / "reports" / "nexus_compile_report_latest.json", {})
    preflight = _read_json(root / "reports" / "nexus_preflight_optimizer_latest.json", {})
    git = _git_status(root)
    phi = _call_phi_advisor(root, intent, call_model)
    compiler_summary = _summarize_compiler(compiler)
    patch_plan = _derive_patch_plan(wound, compiler, phi, git)
    active = wound.get("active_wound", {}) if isinstance(wound, dict) else {}
    status = "pass"
    if compiler_summary.get("status") == "fail" or compiler_summary.get("failed_gates"):
        status = "wound"
    elif active:
        status = "wound"
    if call_model and phi.get("model_status") not in {"ok", "not_requested"}:
        status = "warn" if status == "pass" else status
    packet = {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": MODE,
        "status": status,
        "generated_utc": _utc(),
        "root": str(root),
        "intent": intent,
        "run_gates": bool(run_gates),
        "call_model": bool(call_model),
        "autonomy_policy": AUTONOMY_POLICY,
        "boundary": BOUNDARY,
        "truth_rule": TRUTH_RULE,
        "gate_results": gate_results,
        "wound_summary": {
            "status": wound.get("status") if isinstance(wound, dict) else None,
            "active_wound_key": wound.get("active_wound_key") if isinstance(wound, dict) else None,
            "active_wound_class": wound.get("active_wound_class") if isinstance(wound, dict) else None,
            "repair_surface": active.get("next_repair_surface") if isinstance(active, dict) else None,
        },
        "compiler_summary": compiler_summary,
        "preflight_summary": {
            "status": preflight.get("status") if isinstance(preflight, dict) else None,
            "failed_preflight_gates": preflight.get("failed_preflight_gates", []) if isinstance(preflight, dict) else [],
        },
        "model_channel": {
            "model": "Phi-4 Mini via local Ollama adapter",
            "separate_from_chat": True,
            "microdose": True,
            "model_status": phi.get("model_status"),
            "advice_source": phi.get("advice_source"),
            "command_env": "NEXUS_PHI4_MINI_COMMAND",
        },
        "model_advice": (phi.get("packet", {}) or {}).get("advice", {}) if isinstance(phi.get("packet"), dict) else {},
        "patch_plan": patch_plan,
        "recommended_next_gate": patch_plan.get("next_gate"),
        "repo_status": git,
        "claim_boundary": "Bounded Phi autonomy may run known read-only gates, call local Phi, write evidence, and select the next gate. It may not mutate files, stage, commit, push, read secrets, use external network, or self-authorize durable changes.",
    }
    return packet


def write_phi_microdose_packet(root: str | Path, intent: str = "", run_gates: bool = False, call_model: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_phi_microdose_packet(root, intent, run_gates, call_model)
    _write_json(root / "reports" / "nexus_phi_microdose_loop_latest.json", packet)
    _write_json(root / "state" / "loops" / "nexus_phi_microdose_loop_latest.json", {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "model_status": packet["model_channel"].get("model_status"),
        "advice_source": packet["model_channel"].get("advice_source"),
        "recommended_next_gate": packet.get("recommended_next_gate"),
        "generated_utc": packet["generated_utc"],
    })
    return packet


def render(packet: dict[str, Any]) -> str:
    wound = packet.get("wound_summary", {})
    comp = packet.get("compiler_summary", {})
    model = packet.get("model_channel", {})
    plan = packet.get("patch_plan", {})
    lines = [
        "NEXUS PHI MICRODOSE LOOP",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Wound: {wound.get('active_wound_key') or 'none'} / {wound.get('active_wound_class') or 'none'}",
        f"Compiler: {comp.get('status')} / failed={', '.join(comp.get('failed_gates') or []) or 'none'}",
        f"Model: {model.get('model_status')} / source={model.get('advice_source')}",
        f"Plan: {plan.get('plan_type')} -> {plan.get('repair_surface')}",
        f"Next gate: {packet.get('recommended_next_gate')}",
        "Autonomy: run read-only gates + local Phi + write evidence + choose next gate.",
        "Boundary: no file mutation, no git stage/commit/push, no secrets, no self-authorized durable changes.",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--run-gates", action="store_true")
    parser.add_argument("--call-model", action="store_true")
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    call_model = bool(args.call_model) and not args.no_model
    packet = write_phi_microdose_packet(args.root, args.intent, args.run_gates, call_model)
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else render(packet))
    return 0 if packet.get("status") in {"pass", "warn", "wound"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
