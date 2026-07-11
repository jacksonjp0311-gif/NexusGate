from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.loops.predictive_timing import STEP_ORDER


VERSION = "0.1.0"
SCHEMA = "NEXUS_CERTIFICATE_RESUME.v0.1.0"
REPORT_LATEST = Path("reports") / "nexus_certificate_resume_report_latest.json"
STATE_LATEST = Path("state") / "loops" / "nexus_certificate_resume_latest.json"

CLAIM_BOUNDARY = (
    "Certificate Resume is local development evidence only. It hashes passed gate "
    "evidence to recommend a resume point after failure, but it does not skip final "
    "evolve before commit, prove correctness, mutate the repo, or self-authorize."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "skip_final_evolve_before_commit",
    "claim_pass_from_certificate_only",
    "mutate_repo",
    "git_write",
    "arbitrary_shell_commands",
    "hide_failures",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")
    except Exception:
        return ""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _latest_human_surface(root: Path) -> Path | None:
    base = root / "reports" / "human_surface"
    if not base.exists():
        return None
    sessions = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
    return sessions[0] if sessions else None


def _step_id(path: Path) -> str:
    return path.stem


def _step_status(path: Path) -> str:
    raw = _read_text(path)
    try:
        parsed = json.loads(raw)
        status = str(parsed.get("status", "")).lower()
        if status in {"pass", "warn", "fail", "timeout"}:
            return status
    except Exception:
        pass
    text = raw.lower()
    if "nexus step timeout" in text or "timed out" in text:
        return "timeout"
    if "traceback" in text or '"status": "fail"' in text or " failed" in text:
        return "fail"
    if '"status": "warn"' in text or "warning" in text:
        return "warn"
    return "pass"


def _git_scope_hash(root: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        text = proc.stdout or ""
    except Exception:
        text = ""
    return {
        "dirty_count": len([line for line in text.splitlines() if line.strip()]),
        "scope_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def _certificate_for(root: Path, path: Path, git_scope: dict[str, Any]) -> dict[str, Any]:
    content = path.read_bytes()
    input_fingerprint = hashlib.sha256()
    input_fingerprint.update(_step_id(path).encode("utf-8"))
    input_fingerprint.update(git_scope["scope_hash"].encode("utf-8"))
    input_fingerprint.update(content)
    return {
        "gate": _step_id(path),
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "status": _step_status(path),
        "evidence_sha256": hashlib.sha256(content).hexdigest(),
        "input_fingerprint_sha256": input_fingerprint.hexdigest(),
    }


def build_certificate_resume_packet(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve()
    session = _latest_human_surface(root)
    git_scope = _git_scope_hash(root)
    certificates: list[dict[str, Any]] = []
    failed_gate: dict[str, Any] | None = None
    if session:
        files = sorted([p for p in session.iterdir() if p.is_file()], key=lambda p: p.name)
        ordered = sorted(files, key=lambda p: STEP_ORDER.index(_step_id(p)) if _step_id(p) in STEP_ORDER else 999)
        for file_path in ordered:
            cert = _certificate_for(root, file_path, git_scope)
            if cert["status"] in {"fail", "timeout"} and failed_gate is None:
                failed_gate = cert
                break
            if cert["status"] in {"pass", "warn"}:
                certificates.append(cert)

    resume_gate = failed_gate["gate"] if failed_gate else None
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "certificate_resume",
        "status": "warn" if failed_gate else "pass",
        "generated_utc": _utc(),
        "latest_human_surface": str(session.relative_to(root)).replace("\\", "/") if session else None,
        "git_scope": git_scope,
        "passed_gate_certificates": certificates,
        "certificate_count": len(certificates),
        "failed_gate": failed_gate,
        "recommended_resume_gate": resume_gate,
        "recommended_next_command": (
            f"rerun failed gate {resume_gate} after fixing active wound" if resume_gate else ".\\scripts\\nexus.ps1 predictive-evolve"
        ),
        "final_evolve_required_before_commit": True,
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "skip_final_evolve": False,
            "repo_mutation": False,
            "git_write": False,
            "self_authorize": False,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_outputs(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    _write_json(root_path / REPORT_LATEST, packet)
    _write_json(root_path / STATE_LATEST, {
        "schema": packet["schema"],
        "version": packet["version"],
        "status": packet["status"],
        "generated_utc": packet["generated_utc"],
        "certificate_count": packet["certificate_count"],
        "recommended_resume_gate": packet["recommended_resume_gate"],
        "final_evolve_required_before_commit": packet["final_evolve_required_before_commit"],
        "blocked_actions": packet["blocked_actions"],
        "claim_boundary": packet["claim_boundary"],
    })


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS CERTIFICATE RESUME",
        f"Version: v{packet.get('version')}",
        f"Status: {packet.get('status')}",
        f"Certificates: {packet.get('certificate_count')}",
        f"Resume gate: {packet.get('recommended_resume_gate') or 'none'}",
        "Boundary: certificates recommend resume points; final evolve remains required before commit.",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS certificate resume packet.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = build_certificate_resume_packet(args.root)
    write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
