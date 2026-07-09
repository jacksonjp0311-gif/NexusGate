from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
SCHEMA = "NEXUS_PHI_WOUND_ADVISOR.v1.0.0"
MODE = "nexus_phi_wound_advisor"
BOUNDARY = {
    "repo_mutation_enabled": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
    "patch_apply_enabled": False,
}
TRUTH_RULE = {
    "stdout": "smoke_only",
    "file_packets": "truth",
    "tail": "never_truth",
    "model_output": "advisory_only",
}
ALLOWED_ACTIONS = [
    "diagnose_wound",
    "recommend_patch_surface",
    "emit_patch_plan",
    "emit_next_gate",
]
FORBIDDEN_ACTIONS = [
    "run_shell",
    "stage_git",
    "commit",
    "push",
    "access_network",
    "read_secrets",
    "apply_patch_without_human_authorization",
]


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


def _run(root: Path, args: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, cwd=str(root), capture_output=True, text=True, timeout=timeout, check=False)
        return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": (proc.stdout or "")[-2000:], "stderr": (proc.stderr or "")[-1000:]}
    except Exception as exc:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(exc)}


def _git_status(root: Path) -> dict[str, Any]:
    status = _run(root, ["git", "status", "--short"])
    lines = [line for line in status.get("stdout", "").splitlines() if line.strip()]
    head = _run(root, ["git", "rev-parse", "--short", "HEAD"]).get("stdout", "").strip()
    return {"head": head, "dirty": bool(lines), "changed_count": len(lines), "status_preview": lines[:40]}


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    first = text.find("{")
    last = text.rfind("}")
    if first < 0 or last <= first:
        return None
    try:
        data = json.loads(text[first:last + 1])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _ollama_adapter_command() -> str:
    return f'"{sys.executable}" -m nexus_gate.loops.phi4_ollama_adapter --prompt-file "{{prompt_file}}"'


def _normalize_phi_command(command: str) -> str:
    command = (command or "").strip()
    lowered = command.lower()
    if "launch-phi4minicli.cmd" in lowered or "start-phi4minicli.ps1" in lowered:
        return _ollama_adapter_command()
    return command


def _default_phi_command() -> str:
    env = os.environ.get("NEXUS_PHI4_MINI_COMMAND") or os.environ.get("NEXUS_PHI4_MINI_CMD")
    return _normalize_phi_command(env or "")


def _deterministic_advice(wound_packet: dict[str, Any], preflight_packet: dict[str, Any], intent: str) -> dict[str, Any]:
    active = wound_packet.get("active_wound", {}) if isinstance(wound_packet, dict) else {}
    failed = preflight_packet.get("failed_preflight_gates", []) if isinstance(preflight_packet, dict) else []
    wound_key = active.get("wound_key") or wound_packet.get("active_wound_key") or (",".join(failed) if failed else "none")
    wound_class = active.get("wound_class") or wound_packet.get("active_wound_class") or (failed[0] if failed else "no_active_wound")
    repair_surface = active.get("next_repair_surface") or "wound_compression_or_preflight_evidence"
    if "lineage" in str(wound_key).lower() or "generated_for" in str(active).lower():
        repair_surface = "tests or registry generated_for compatibility set"
    if "readme" in str(wound_class).lower():
        repair_surface = "README.md and exact README contract test"
    return {
        "diagnosis": f"Active wound class: {wound_class}; key: {wound_key}.",
        "repair_surface": repair_surface,
        "repair_type": "bounded_patch_plan_only",
        "patch_intent": "Patch the smallest file surface named by file-backed evidence, then rerun the failed gate.",
        "rerun_gate": "python -m unittest discover -s tests",
        "confidence": 0.55 if wound_key != "none" else 0.35,
        "requires_human_authorization": True,
        "source": "deterministic_fallback",
        "intent": intent,
    }


def _build_prompt(packet: dict[str, Any]) -> str:
    compact = {
        "role": "local_phi4_mini_wound_advisor",
        "instruction": "Return ONLY compact JSON. Diagnose the wound, name the smallest repair surface, propose the next gate. Do not ask for shell access. Do not claim authority.",
        "allowed_actions": ALLOWED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "truth_rule": TRUTH_RULE,
        "active_wound": packet.get("active_wound"),
        "preflight_failed_gates": packet.get("preflight_failed_gates"),
        "repo_status": packet.get("repo_status"),
        "intent": packet.get("intent"),
        "required_json_keys": ["diagnosis", "repair_surface", "repair_type", "patch_intent", "rerun_gate", "confidence", "requires_human_authorization"],
    }
    return json.dumps(compact, indent=2, sort_keys=True)


def _call_phi(command: str, prompt: str, timeout: int = 90) -> dict[str, Any]:
    command = _normalize_phi_command(command)
    if not command:
        return {"ok": False, "status": "not_configured", "error": "Set NEXUS_PHI4_MINI_COMMAND to a local Phi-4 Mini command.", "raw_preview": ""}
    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".json") as fh:
            fh.write(prompt)
            prompt_file = fh.name
        cmd = command.replace("{prompt_file}", prompt_file).replace("{prompt}", prompt.replace('"', '\\"'))
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, shell=True, check=False)
        raw = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        parsed = _extract_json(raw)
        return {
            "ok": proc.returncode == 0 and parsed is not None,
            "status": "ok" if proc.returncode == 0 and parsed is not None else "unparsed_or_nonzero",
            "returncode": proc.returncode,
            "command_preview": cmd[:240],
            "raw_preview": raw[-2000:],
            "parsed": parsed,
        }
    except Exception as exc:
        return {"ok": False, "status": "error", "error": str(exc), "command_preview": command[:240], "raw_preview": ""}
    finally:
        if prompt_file:
            try:
                Path(prompt_file).unlink(missing_ok=True)
            except Exception:
                pass


def build_phi_wound_advisor_packet(root: str | Path, intent: str = "", call_model: bool = False, require_model: bool = False, phi_command: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    wound_path = root / "reports" / "nexus_wound_compression_latest.json"
    preflight_path = root / "reports" / "nexus_preflight_optimizer_latest.json"
    bounded_path = root / "reports" / "nexus_bounded_runtime_report_latest.json"
    compiler_path = root / "reports" / "nexus_compile_report_latest.json"
    wound = _read_json(wound_path, {})
    preflight = _read_json(preflight_path, {})
    bounded = _read_json(bounded_path, {})
    compiler = _read_json(compiler_path, {})
    git = _git_status(root)
    active = wound.get("active_wound", {}) if isinstance(wound, dict) else {}
    preflight_failed = preflight.get("failed_preflight_gates", []) if isinstance(preflight, dict) else []
    skeleton = {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": MODE,
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "active_wound": active,
        "active_wound_key": wound.get("active_wound_key") if isinstance(wound, dict) else None,
        "active_wound_class": wound.get("active_wound_class") if isinstance(wound, dict) else None,
        "preflight_failed_gates": preflight_failed,
        "repo_status": git,
    }
    prompt = _build_prompt(skeleton)
    deterministic = _deterministic_advice(wound, preflight, intent)
    phi_result = {"ok": False, "status": "not_requested", "raw_preview": "", "parsed": None}
    if call_model:
        phi_result = _call_phi(phi_command or _default_phi_command(), prompt)
    model_advice = phi_result.get("parsed") if isinstance(phi_result.get("parsed"), dict) else None
    advice = model_advice or deterministic
    model_status = phi_result.get("status", "not_requested")
    status = "advice"
    if require_model and not phi_result.get("ok"):
        status = "model_unavailable"
    packet = {
        **skeleton,
        "status": status,
        "model_channel": {
            "model": "Phi-4 Mini base local/GPU if configured",
            "separate_from_chat": True,
            "microdose": True,
            "call_requested": bool(call_model),
            "require_model": bool(require_model),
            "model_status": model_status,
            "command_env": "NEXUS_PHI4_MINI_COMMAND",
        },
        "phi_result": {k: v for k, v in phi_result.items() if k != "parsed"},
        "advice": advice,
        "recommended_next_loop": "wound-indexed-resume" if (active or preflight_failed) else "evolution-radar",
        "recommended_next_command": advice.get("rerun_gate", ".\\scripts\\nexus.ps1 wound-compress"),
        "self_heal_policy": {
            "current_mode": "advisor_only",
            "patch_apply_enabled": False,
            "human_authorization_required": True,
            "deterministic_controller_must_verify": True,
            "future_modes": ["patch_plan", "human_authorized_self_heal"],
        },
        "allowed_actions": ALLOWED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "truth_rule": TRUTH_RULE,
        "truth_sources": {
            "wound_report_exists": wound_path.exists(),
            "preflight_report_exists": preflight_path.exists(),
            "bounded_report_exists": bounded_path.exists(),
            "compiler_report_exists": compiler_path.exists(),
            "bounded_status": bounded.get("status") if isinstance(bounded, dict) else None,
            "compiler_status": compiler.get("status") if isinstance(compiler, dict) else None,
        },
        "boundary": BOUNDARY,
        "claim_boundary": "Phi Wound Advisor is a local read-only advisory lane. Phi recommends; NexusGate verifies; human authorizes durable mutation; compiler decides trust.",
    }
    return packet


def write_phi_wound_advisor(root: str | Path, intent: str = "", call_model: bool = False, require_model: bool = False, phi_command: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_phi_wound_advisor_packet(root, intent, call_model, require_model, phi_command)
    _write_json(root / "reports" / "nexus_phi_wound_advisor_latest.json", packet)
    _write_json(root / "state" / "loops" / "nexus_phi_wound_advisor.v1.0.0.json", packet)
    _write_json(root / "state" / "loops" / "nexus_phi_wound_advisor_latest.json", {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "model_status": packet["model_channel"]["model_status"],
        "active_wound_key": packet.get("active_wound_key"),
        "recommended_next_loop": packet.get("recommended_next_loop"),
        "generated_utc": packet["generated_utc"],
    })
    return packet


def render(packet: dict[str, Any]) -> str:
    advice = packet.get("advice", {})
    lines = [
        "NEXUS PHI WOUND ADVISOR",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"HEAD: {packet.get('repo_status', {}).get('head', 'unknown')}",
        f"Model status: {packet.get('model_channel', {}).get('model_status')}",
        f"Separate from ChatGPT: {packet.get('model_channel', {}).get('separate_from_chat')}",
        f"Active wound: {packet.get('active_wound_key')}",
        f"Diagnosis: {advice.get('diagnosis')}",
        f"Repair surface: {advice.get('repair_surface')}",
        f"Rerun gate: {advice.get('rerun_gate')}",
        "Boundary: advisor-only; no autonomous authority; no git write authority.",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--call-model", action="store_true")
    parser.add_argument("--require-model", action="store_true")
    parser.add_argument("--phi-command", default="")
    args = parser.parse_args(argv)
    packet = write_phi_wound_advisor(args.root, args.intent, args.call_model, args.require_model, args.phi_command)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    if args.require_model and packet.get("status") == "model_unavailable":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
