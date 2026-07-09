
from __future__ import annotations
import argparse
import datetime as _dt
import json
import subprocess
from pathlib import Path
from typing import Any

VERSION = "0.9.8"
SCHEMA = "NEXUS_WOUND_COMPRESSION.v0.9.8"
MODE = "nexus_wound_compression_engine"
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
TRUTH_RULE = {
    "stdout": "smoke_only",
    "file_packets": "truth",
    "bounded_report": "reports/nexus_bounded_runtime_report_latest.json",
    "compiler_report": "reports/nexus_compile_report_latest.json",
    "tail": "never_truth",
}


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


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
        return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-2000:]}
    except Exception as exc:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(exc)}


def _classify_test_failure(file_name: str, stderr: str, stdout: str) -> str:
    joined = f"{file_name}\n{stderr}\n{stdout}".lower()
    if "test_readme_freshness" in joined:
        return "readme_freshness_contract"
    if "readme" in joined:
        return "readme_marker_or_readme_contract"
    if "modulenotfounderror" in joined:
        return "missing_python_module"
    if "jsondecodeerror" in joined:
        return "json_contract_or_stdout_tail_misread"
    if "parsererror" in joined or "missing '{'" in joined or "missing closing '}'" in joined:
        return "powershell_parse_contract"
    return "python_test_failure"


def _extract_bounded_failure(packet: dict[str, Any]) -> dict[str, Any] | None:
    if packet.get("status") != "fail":
        return None
    failures = packet.get("failures") or []
    if not failures:
        failures = [item for item in packet.get("results_tail", []) if isinstance(item, dict) and item.get("returncode")]
    if not failures:
        return {
            "source": "bounded_tests",
            "wound_class": "bounded_unknown_failure",
            "wound_key": "bounded:unknown",
            "failed_files": [],
            "evidence_preview": "bounded report failed without failures[] payload",
        }
    first = failures[0]
    file_name = str(first.get("file", "unknown"))
    stderr = str(first.get("stderr_tail", ""))
    stdout = str(first.get("stdout_tail", ""))
    wound_class = _classify_test_failure(file_name, stderr, stdout)
    return {
        "source": "bounded_tests",
        "wound_class": wound_class,
        "wound_key": f"bounded:{file_name}:{wound_class}",
        "failed_files": [str(item.get("file", "unknown")) for item in failures if isinstance(item, dict)],
        "failed_count": len(failures),
        "evidence_preview": (stderr or stdout)[-1200:],
        "next_repair_surface": file_name if wound_class.startswith("readme") else "source_or_test_named_by_failed_file",
    }


def _extract_compiler_failure(packet: dict[str, Any]) -> dict[str, Any] | None:
    if packet.get("status") != "fail":
        return None
    gates = packet.get("gates") or []
    failed = [g for g in gates if isinstance(g, dict) and g.get("status") == "fail"]
    names = [str(g.get("gate") or g.get("name") or "unknown") for g in failed]
    return {
        "source": "compiler",
        "wound_class": "compiler_gate_failure",
        "wound_key": "compiler:" + ",".join(names[:5]) if names else "compiler:unknown",
        "failed_gates": names,
        "failed_count": len(failed),
        "evidence_preview": json.dumps(failed[:2], sort_keys=True)[-1200:] if failed else "compiler failed without failed gate list",
        "next_repair_surface": "compiler_failed_gate_evidence",
    }


def _git_status(root: Path) -> dict[str, Any]:
    status = _run(root, ["git", "status", "--short"])
    lines = [line for line in status.get("stdout", "").splitlines() if line.strip()]
    head = _run(root, ["git", "rev-parse", "--short", "HEAD"]).get("stdout", "").strip()
    return {"head": head, "dirty": bool(lines), "changed_count": len(lines), "status_preview": lines[:50]}


def build_wound_compression_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    bounded_path = root / "reports" / "nexus_bounded_runtime_report_latest.json"
    compiler_path = root / "reports" / "nexus_compile_report_latest.json"
    toolbelt_path = root / "reports" / "nexus_toolbelt_latest.json"
    bounded = _read_json(bounded_path, {})
    compiler = _read_json(compiler_path, {})
    toolbelt = _read_json(toolbelt_path, {})
    git = _git_status(root)

    active = _extract_bounded_failure(bounded) or _extract_compiler_failure(compiler)
    if active is None and git.get("dirty"):
        active = {
            "source": "git_status",
            "wound_class": "local_change_surface",
            "wound_key": "git:dirty_worktree",
            "failed_files": [],
            "evidence_preview": "\n".join(git.get("status_preview", []))[-1200:],
            "next_repair_surface": "scope_hygiene_or_stage_policy",
        }
    if active is None:
        active = {
            "source": "none",
            "wound_class": "no_active_wound",
            "wound_key": "none",
            "failed_files": [],
            "evidence_preview": "No bounded/compiler/git wound detected from current evidence packets.",
            "next_repair_surface": "evolution_radar",
        }

    active_bool = active.get("wound_class") != "no_active_wound"
    recommended = "compiler-wound-focus" if active.get("source") == "compiler" else "wound-indexed-resume" if active_bool else "evolution-radar"
    tag = intent or active.get("wound_key", "<intent>")
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": MODE,
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "status": "wound" if active_bool else "pass",
        "active_wound": active,
        "active_wound_key": active.get("wound_key"),
        "active_wound_class": active.get("wound_class"),
        "recommended_next_loop": recommended,
        "recommended_next_command": f'.\\scripts\\nexus.ps1 meta-loop -Loop {recommended} -Tag "{tag}"',
        "repair_strategy": "resume_from_active_wound_only; preserve_green_gates; use_file_packets_as_truth",
        "preserve_green_gates": True,
        "truth_rule": TRUTH_RULE,
        "truth_sources": {
            "bounded_report_exists": bounded_path.exists(),
            "compiler_report_exists": compiler_path.exists(),
            "toolbelt_report_exists": toolbelt_path.exists(),
        },
        "repo_status": git,
        "upstream_toolbelt": {"schema": toolbelt.get("schema"), "version": toolbelt.get("version"), "status": toolbelt.get("status")},
        "boundary": BOUNDARY,
        "claim_boundary": "Wound Compression is a read-only evidence reducer. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
    }


def write_wound_compression(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_wound_compression_packet(root, intent)
    _write_json(root / "reports" / "nexus_wound_compression_latest.json", packet)
    _write_json(root / "state" / "loops" / "nexus_wound_compression_latest.json", {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "active_wound_key": packet["active_wound_key"],
        "active_wound_class": packet["active_wound_class"],
        "recommended_next_loop": packet["recommended_next_loop"],
        "generated_utc": packet["generated_utc"],
    })
    return packet


def render(packet: dict[str, Any]) -> str:
    wound = packet.get("active_wound", {})
    lines = [
        "NEXUS WOUND COMPRESSION ENGINE",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"HEAD: {packet.get('repo_status', {}).get('head', 'unknown')}",
        f"Active wound: {packet.get('active_wound_key')}",
        f"Class: {packet.get('active_wound_class')}",
        f"Source: {wound.get('source')}",
        f"Next loop: {packet.get('recommended_next_loop')}",
        f"Next command: {packet.get('recommended_next_command')}",
        "Truth: stdout=smoke only; reports/state files=evidence; tails=never truth",
        "Boundary: read-only; no autonomous authority; no git write authority.",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_wound_compression(args.root, args.intent)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
