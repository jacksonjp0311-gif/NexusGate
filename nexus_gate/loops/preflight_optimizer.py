from __future__ import annotations
import argparse
import datetime as _dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any

VERSION = "0.9.9"
SCHEMA = "NEXUS_PREFLIGHT_OPTIMIZER.v0.9.9"
MODE = "nexus_preflight_optimizer"
BOUNDARY = {
    "repo_mutation_enabled": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
}
REQUIRED_COMMANDS = ["toolbelt", "toolbelt-json", "wound-compress", "preflight", "preflight-json"]
TOOLBELT_KEYS = ["schema", "version", "repo_status", "recommended_next_loop", "next_command", "recommended_next_command", "process_chains", "boundary"]
WOUND_KEYS = ["schema", "version", "status", "active_wound", "active_wound_key", "truth_rule", "recommended_next_loop", "boundary"]


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(_read(path)) if path.exists() else default
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


def _gate(status: str, evidence: Any = None) -> dict[str, Any]:
    return {"status": status, "evidence": evidence or {}}


def check_command_surface(root: Path) -> dict[str, Any]:
    ps = _read(root / "scripts" / "nexus.ps1")
    sh = _read(root / "scripts" / "nexus.sh")
    missing_ps = [c for c in REQUIRED_COMMANDS if f'"{c}"' not in ps and f"'{c}'" not in ps]
    missing_sh = [c for c in REQUIRED_COMMANDS if c not in sh]
    duplicate_case_tokens = []
    for token in REQUIRED_COMMANDS:
        count = len(re.findall(rf"(^|\n)\s*{re.escape(token)}\)", sh))
        if count > 1:
            duplicate_case_tokens.append(token)
    status = "pass" if not missing_ps and not missing_sh else "fail"
    if status == "pass" and duplicate_case_tokens:
        status = "warn"
    return _gate(status, {"missing_powershell": missing_ps, "missing_bash": missing_sh, "duplicate_bash_cases": duplicate_case_tokens})


def check_readme_current_line(root: Path) -> dict[str, Any]:
    text = _read(root / "README.md")
    semantic_versions = []
    for major, minor, patch in re.findall(r"v(\d+)\.(\d+)\.(\d+)", text):
        semantic_versions.append((int(major), int(minor), int(patch)))
    latest = max(semantic_versions, default=(0, 9, 0))
    expected = f"v{latest[0]}.{latest[1]}.{latest[2]}"
    current_line_match = re.search(r"NEXUS GATE current line:\s*([^\n]+)", text)
    current_line = current_line_match.group(1).strip() if current_line_match else "missing"
    needs = ["Preflight Optimizer", "NEXUS_PREFLIGHT_OPTIMIZER.md"]
    if latest >= (1, 0, 0):
        needs += ["Phi Wound Advisor", "NEXUS_PHI_WOUND_ADVISOR.md"]
    missing = [item for item in needs if item not in text]
    ok = expected in current_line and not missing
    return _gate("pass" if ok else "fail", {
        "expected_latest": expected,
        "latest_tuple": list(latest),
        "current_line": current_line,
        "line_count": len(text.splitlines()),
        "missing": missing,
        "accepted_current_line_versions": ["v0.9.9", "v1.0.0+"],
    })


def check_packet_contracts(root: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    try:
        from nexus_gate.loops.toolbelt import build_toolbelt_packet
        toolbelt = build_toolbelt_packet(root, "preflight", "dashboard")
        evidence["toolbelt_missing"] = [k for k in TOOLBELT_KEYS if k not in toolbelt]
        evidence["toolbelt_schema"] = toolbelt.get("schema")
        evidence["toolbelt_version"] = toolbelt.get("version")
    except Exception as exc:
        evidence["toolbelt_error"] = str(exc)
    try:
        from nexus_gate.loops.wound_compression import build_wound_compression_packet
        wound = build_wound_compression_packet(root, "preflight")
        evidence["wound_missing"] = [k for k in WOUND_KEYS if k not in wound]
        evidence["wound_schema"] = wound.get("schema")
        evidence["wound_version"] = wound.get("version")
    except Exception as exc:
        evidence["wound_error"] = str(exc)
    fail = evidence.get("toolbelt_error") or evidence.get("wound_error") or evidence.get("toolbelt_missing") or evidence.get("wound_missing")
    return _gate("fail" if fail else "pass", evidence)


def check_bounded_report_shape(root: Path) -> dict[str, Any]:
    path = root / "reports" / "nexus_bounded_runtime_report_latest.json"
    packet = _read_json(path, {})
    if not packet:
        return _gate("warn", {"exists": False, "path": str(path), "reason": "bounded report has not been emitted yet"})

    status = packet.get("status")
    test_count = packet.get("test_count")
    if test_count is None:
        test_count = packet.get("executed_count")
    if test_count is None and isinstance(packet.get("files"), list):
        test_count = len(packet.get("files") or [])

    failures = packet.get("failures")
    results_tail = packet.get("results_tail")
    has_failure_evidence = isinstance(failures, list) or isinstance(results_tail, list)

    notes = []
    if status not in {"pass", "fail", "warn", "review"}:
        notes.append("unknown_status")
    if status == "fail" and not has_failure_evidence:
        return _gate("fail", {
            "exists": True,
            "status": status,
            "test_count": test_count,
            "missing": ["failures_or_results_tail_for_failed_report"],
            "reason": "failed bounded reports must include failure evidence for wound compression",
        })

    # Compatibility rule: a passing bounded report can be compact. Some older
    # packets only preserve status/executed_count and omit failures/results_tail.
    # That is still acceptable because there is no active wound to extract.
    return _gate("pass", {
        "exists": True,
        "status": status,
        "test_count": test_count,
        "has_failures_list": isinstance(failures, list),
        "has_results_tail": isinstance(results_tail, list),
        "notes": notes,
        "accepted_shapes": ["full_bounded_packet", "compact_passing_bounded_packet"],
    })


def check_ignored_stage_risk(root: Path) -> dict[str, Any]:
    intended = [
        "nexus_gate/loops/preflight_optimizer.py",
        "tests/test_preflight_optimizer_v099.py",
        "docs/runtime/NEXUS_PREFLIGHT_OPTIMIZER.md",
        "state/loops/nexus_preflight_optimizer_latest.json",
        "reports/nexus_preflight_optimizer_latest.json",
    ]
    ignored = []
    for rel in intended:
        proc = _run(root, ["git", "check-ignore", "-v", rel], timeout=10)
        if proc.get("returncode") == 0:
            ignored.append({"path": rel, "rule": proc.get("stdout", "").strip()})
    return _gate("warn" if ignored else "pass", {"ignored_intended": ignored, "force_add_required": [x["path"] for x in ignored if x["path"].startswith("state/") or x["path"].startswith("tests/")]})


def build_preflight_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    gates = {
        "command_surface_parity": check_command_surface(root),
        "readme_current_line": check_readme_current_line(root),
        "packet_contracts": check_packet_contracts(root),
        "bounded_report_shape": check_bounded_report_shape(root),
        "ignored_stage_risk": check_ignored_stage_risk(root),
    }
    fail = [name for name, gate in gates.items() if gate.get("status") == "fail"]
    warn = [name for name, gate in gates.items() if gate.get("status") == "warn"]
    next_loop = "wound-indexed-resume" if fail else "scope-hygiene" if warn else "evolution-radar"
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": MODE,
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "status": "fail" if fail else "warn" if warn else "pass",
        "failed_preflight_gates": fail,
        "warning_preflight_gates": warn,
        "gates": gates,
        "recommended_next_loop": next_loop,
        "recommended_next_command": f'.\\scripts\\nexus.ps1 meta-loop -Loop {next_loop} -Tag "{intent or "preflight"}"',
        "truth_rule": {"stdout": "smoke_only", "file_packets": "truth", "tail": "never_truth"},
        "boundary": BOUNDARY,
        "claim_boundary": "Preflight Optimizer is a read-only mutation-surface predictor. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
    }


def write_preflight_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_preflight_packet(root, intent)
    _write_json(root / "reports" / "nexus_preflight_optimizer_latest.json", packet)
    _write_json(root / "state" / "loops" / "nexus_preflight_optimizer_latest.json", {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "failed_preflight_gates": packet["failed_preflight_gates"],
        "warning_preflight_gates": packet["warning_preflight_gates"],
        "recommended_next_loop": packet["recommended_next_loop"],
        "generated_utc": packet["generated_utc"],
    })
    return packet


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS PREFLIGHT OPTIMIZER",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Failed gates: {', '.join(packet.get('failed_preflight_gates') or []) or 'none'}",
        f"Warnings: {', '.join(packet.get('warning_preflight_gates') or []) or 'none'}",
        f"Next loop: {packet.get('recommended_next_loop')}",
        f"Next command: {packet.get('recommended_next_command')}",
        "Truth: stdout=smoke only; reports/state files=evidence; tails=never truth",
        "Boundary: read-only; no autonomous authority; no git write authority.",
    ])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_preflight_packet(args.root, args.intent)
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
