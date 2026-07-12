from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "NEXUS_CORTEX_REFRESH.v1.2.1"
VERSION = "1.2.1"
REPORT_LATEST = Path("reports") / "nexus_cortex_refresh_report_latest.json"

CLAIM_BOUNDARY = (
    "Cortex refresh is local development evidence only. It refreshes Cortex's "
    "repo-local index, graph, telemetry, vector format, and verification "
    "certificate, then emits read-only NEXUS context. It does not grant mutation "
    "authority, prove retrieval correctness, prove safety/security/production "
    "readiness, access secrets, write external APIs, or replace NEXUS gates."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "repo_mutation_from_cortex",
    "bypass_nexus_gates",
    "git_write",
    "external_api_writes",
    "secret_access",
    "arbitrary_shell_commands",
    "autonomous_memory_promotion",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(engine: Path, home: Path, args: list[str], timeout: int = 180) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "-m", "cortex", "--home", str(home), *args, "--json"],
        cwd=engine,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    duration = round(time.perf_counter() - started, 3)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "ok": False,
            "stdout_tail": completed.stdout[-1200:],
            "stderr_tail": completed.stderr[-1200:],
        }
    return {
        "command": " ".join(["python", "-m", "cortex", *args, "--json"]),
        "returncode": completed.returncode,
        "duration_seconds": duration,
        "status": "pass" if completed.returncode == 0 else "fail",
        "payload": payload,
    }


def _step_summary(step: dict[str, Any]) -> dict[str, Any]:
    payload = step.get("payload") or {}
    return {
        "command": step.get("command"),
        "status": step.get("status"),
        "returncode": step.get("returncode"),
        "duration_seconds": step.get("duration_seconds"),
        "keys": sorted(payload.keys())[:20] if isinstance(payload, dict) else [],
    }


def _compact_evidence(packet_payload: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = packet_payload.get("evidence") or []
    compact = []
    for item in evidence[:8]:
        compact.append(
            {
                "path": item.get("path"),
                "kind": item.get("kind"),
                "score": item.get("score"),
                "line_range": item.get("line_range"),
                "content_hash": item.get("content_hash"),
            }
        )
    return compact


def _is_read_only_authority(authority: dict[str, Any]) -> bool:
    if not isinstance(authority, dict):
        return False
    mutating_flags = [
        authority.get("cortex_may_mutate"),
        authority.get("cortex_may_mutate_repo"),
        authority.get("cortex_may_authorize_mutation"),
        authority.get("may_mutate"),
        authority.get("mutation_authority"),
        authority.get("repo_mutation"),
        authority.get("git_write"),
        authority.get("external_api_writes"),
        authority.get("secret_access"),
    ]
    explicitly_blocked = any(value is False for value in mutating_flags)
    no_granted_mutation = not any(value is True for value in mutating_flags)
    mode = str(authority.get("mode") or authority.get("governor_mode") or "").lower()
    bounded_mode = mode in {"", "read_only", "recommend_only", "recommendation_only"}
    return explicitly_blocked and no_granted_mutation and bounded_mode


def refresh_cortex(root: str | Path, intent: str = "", repo: str = "nexus-gate") -> dict[str, Any]:
    root_path = Path(root).resolve()
    engine = root_path / "Cortex"
    home = root_path / "state" / "cortex_memory"
    task = intent or "Refresh Cortex certificate for NEXUS predictive memory orchestration."

    steps: list[dict[str, Any]] = []
    if not engine.is_dir():
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "system": "NEXUS GATE",
            "mode": "cortex_refresh",
            "status": "fail",
            "generated_utc": _utc(),
            "repo": repo,
            "steps": [],
            "checks": {"engine_present": False},
            "blocked_actions": BLOCKED_ACTIONS,
            "claim_boundary": CLAIM_BOUNDARY,
        }

    sequence = [
        ("index", ["index", "--repo", repo, "--force"], 240),
        ("telemetry", ["telemetry", "--repo", repo], 180),
        ("graph", ["graph", "--repo", repo, "--rebuild"], 180),
        ("migrate_vectors", ["migrate-vectors", "--repo", repo], 180),
        ("verify", ["verify", "--repo", repo], 180),
        ("activate", ["activate", "--repo", repo, "--task", task, "--refresh", "always"], 240),
        ("doctor", ["doctor", "--repo", repo], 180),
        ("nexus_packet", ["nexus-packet", "--repo", repo, "--task", task], 180),
    ]

    for step_id, args, timeout in sequence:
        result = _run(engine, home, args, timeout=timeout)
        result["step_id"] = step_id
        steps.append(result)
        if result["returncode"] != 0:
            break

    by_id = {step["step_id"]: step for step in steps}
    verify_payload = (by_id.get("verify") or {}).get("payload") or {}
    doctor_payload = (by_id.get("doctor") or {}).get("payload") or {}
    packet_payload = (by_id.get("nexus_packet") or {}).get("payload") or {}
    vector_format = doctor_payload.get("vector_format") or {}
    governor = doctor_payload.get("governor") or {}
    components = governor.get("components") or {}
    checks = {
        "engine_present": engine.is_dir(),
        "all_steps_passed": all(step.get("returncode") == 0 for step in steps) and len(steps) == len(sequence),
        "certificate_verified": verify_payload.get("status") == "verified",
        "manifest_current": bool((verify_payload.get("manifest") or {}).get("current")),
        "database_integrity": bool(doctor_payload.get("database_integrity")),
        "vector_storage_current": vector_format.get("legacy_or_invalid", 0) == 0,
        "governor_read_only_or_bounded": governor.get("mode") in {"read_only", "normal", "constrained"},
        "governor_integrity": components.get("integrity"),
        "packet_shape": all(key in packet_payload for key in ("intent", "evidence", "authority", "context")),
        "read_only_authority": _is_read_only_authority(packet_payload.get("authority", {})),
    }
    status = "ready" if all(
        checks[key]
        for key in (
            "all_steps_passed",
            "certificate_verified",
            "manifest_current",
            "database_integrity",
            "vector_storage_current",
            "packet_shape",
            "read_only_authority",
        )
    ) else "constrained" if steps else "fail"

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "cortex_refresh",
        "status": status,
        "generated_utc": _utc(),
        "repo": repo,
        "intent": task,
        "read_surfaces": [
            "Cortex/",
            "state/cortex_memory/",
            "git history via Cortex telemetry",
        ],
        "write_surfaces": [
            "state/cortex_memory/",
            ".cortex/bootstrap_certificate.json",
            REPORT_LATEST.as_posix(),
        ],
        "step_summaries": [_step_summary(step) for step in steps],
        "checks": checks,
        "certificate": {
            "status": verify_payload.get("status"),
            "certificate_hash": verify_payload.get("certificate_hash"),
            "coverage": verify_payload.get("coverage"),
            "manifest": verify_payload.get("manifest"),
        },
        "doctor": {
            "database_integrity": doctor_payload.get("database_integrity"),
            "governor": governor,
            "vector_format": vector_format,
            "neural_ledger_integrity": doctor_payload.get("neural_ledger_integrity"),
        },
        "nexus_packet": {
            "schema_version": packet_payload.get("schema_version"),
            "intent": packet_payload.get("intent"),
            "authority": packet_payload.get("authority"),
            "evidence": _compact_evidence(packet_payload),
            "context": {
                "repository": (packet_payload.get("context") or {}).get("repository"),
                "estimated_tokens": (packet_payload.get("context") or {}).get("estimated_tokens"),
                "neural_interlink": {
                    "metrics": (((packet_payload.get("context") or {}).get("neural_interlink") or {}).get("metrics")),
                    "fired_paths": (((packet_payload.get("context") or {}).get("neural_interlink") or {}).get("fired_paths") or [])[:20],
                },
            },
        },
        "next_action": ".\\scripts\\nexus.ps1 predictive-memory",
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "cortex_may_mutate_repo": False,
            "git_write": False,
            "external_api_writes": False,
            "secret_access": False,
            "final_nexus_evolve_required": True,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_report(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    path = root_path / REPORT_LATEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render(packet: dict[str, Any]) -> str:
    checks = packet.get("checks") or {}
    return "\n".join(
        [
            "NEXUS CORTEX REFRESH",
            f"Version: v{packet.get('version')}",
            f"Status: {packet.get('status')}",
            f"Certificate: {checks.get('certificate_verified')}",
            f"Manifest current: {checks.get('manifest_current')}",
            f"Vector current: {checks.get('vector_storage_current')}",
            f"Next: {packet.get('next_action')}",
            "Boundary: refreshes Cortex evidence only; NEXUS gates and human authority remain controlling.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh NEXUS Cortex evidence and certificate.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--repo", default="nexus-gate")
    parser.add_argument("--intent", default="Refresh Cortex certificate for NEXUS predictive memory orchestration.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = refresh_cortex(args.root, intent=args.intent, repo=args.repo)
    write_report(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"ready", "constrained"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
