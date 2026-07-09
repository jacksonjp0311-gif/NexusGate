from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.loops import phi_gate_supervisor


SCHEMA = "NEXUS_PHI_GATE_SUPERVISOR_COMPILE.v1.1.2"
VERSION = "1.1.2"
REPORT_LATEST = Path("reports") / "nexus_phi_gate_supervisor_report_latest.json"
REPORT_VERSIONED = Path("reports") / "nexus_phi_gate_supervisor_report.v1.1.2.json"

REQUIRED_PATHS = [
    Path("docs/runtime/NEXUS_PHI_GATE_SUPERVISOR.md"),
    Path("nexus_gate/loops/phi_gate_supervisor.py"),
    Path("tests/test_phi_gate_supervisor_v111.py"),
    Path("state/loops/nexus_phi_gate_supervisor.v1.1.1.json"),
    Path("state/loops/nexus_phi_gate_supervisor_compile.v1.1.2.json"),
    Path("loops/nexus_loop_registry.v0.1.json"),
    Path("state/loops/nexus_loop_registry.v0.1.json"),
]

REQUIRED_BLOCKED_MARKERS = [
    "arbitrary_command_execution",
    "autonomous_authority",
    "git_push_enabled",
    "secrets_enabled",
    "repo_mutation_enabled_without_human_authorization",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8-sig")


def _check_path(root: Path, path: Path) -> dict[str, Any]:
    return {"name": f"path:{path.as_posix()}", "status": "pass" if (root / path).exists() else "fail"}


def _check_contains(root: Path, path: Path, marker: str, name: str | None = None) -> dict[str, Any]:
    exists = (root / path).exists()
    found = exists and marker in _read_text(root, path)
    return {
        "name": name or f"contains:{path.as_posix()}:{marker}",
        "status": "pass" if found else "fail",
        "path": path.as_posix(),
        "marker": marker,
    }


def compile_report(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []
    checks.extend(_check_path(root, path) for path in REQUIRED_PATHS)

    checks.append(_check_contains(root, Path("scripts/nexus.ps1"), "phi-gate-compile", "powershell exposes phi-gate-compile"))
    checks.append(_check_contains(root, Path("scripts/nexus.sh"), "phi-gate-compile", "bash exposes phi-gate-compile"))
    checks.append(_check_contains(root, Path("scripts/nexus.ps1"), "--auto-repair", "powershell uses auto-repair"))
    checks.append(_check_contains(root, Path("scripts/nexus.sh"), "--auto-repair", "bash uses auto-repair"))
    checks.append(_check_contains(root, Path("loops/nexus_loop_registry.v0.1.json"), "--auto-repair", "loop registry uses auto-repair"))
    checks.append(_check_contains(root, Path("state/loops/nexus_loop_registry.v0.1.json"), "--auto-repair", "state loop registry uses auto-repair"))
    checks.append(_check_contains(root, Path("scripts/nexus.ps1"), "--call-model", "powershell uses call-model"))
    checks.append(_check_contains(root, Path("scripts/nexus.sh"), "--call-model", "bash uses call-model"))
    checks.append(_check_contains(root, Path("loops/nexus_loop_registry.v0.1.json"), "--call-model", "loop registry uses call-model"))
    checks.append(_check_contains(root, Path("state/loops/nexus_loop_registry.v0.1.json"), "--call-model", "state loop registry uses call-model"))

    bad_self_heal = []
    bad_legacy_flags = []
    for path in [Path("scripts/nexus.ps1"), Path("scripts/nexus.sh"), Path("loops/nexus_loop_registry.v0.1.json"), Path("state/loops/nexus_loop_registry.v0.1.json")]:
        text = _read_text(root, path) if (root / path).exists() else ""
        if "--self-heal" in text:
            bad_self_heal.append(path.as_posix())
        if "--call-phi" in text:
            bad_legacy_flags.append(path.as_posix())
    checks.append({"name": "legacy self-heal flag removed from supervisor command surfaces", "status": "pass" if not bad_self_heal else "fail", "matches": bad_self_heal})
    checks.append({"name": "legacy call-phi flag removed from supervisor command surfaces", "status": "pass" if not bad_legacy_flags else "fail", "matches": bad_legacy_flags})

    boundary = phi_gate_supervisor.AUTHORITY_BOUNDARY
    for marker in REQUIRED_BLOCKED_MARKERS:
        checks.append({"name": f"authority boundary:{marker}", "status": "pass" if marker in boundary and boundary[marker] is False else "fail"})

    checks.append({
        "name": "deterministic allowlisted repairs only",
        "status": "pass" if boundary.get("deterministic_allowlisted_repairs_only") is True else "fail",
    })
    checks.append({
        "name": "allowed repair lanes declared",
        "status": "pass" if len(phi_gate_supervisor.ALLOWED_REPAIR_LANES) >= 5 else "fail",
        "lanes": sorted(phi_gate_supervisor.ALLOWED_REPAIR_LANES),
    })
    checks.append(_check_contains(root, Path("docs/runtime/NEXUS_PHI_GATE_SUPERVISOR.md"), "The human authorizes durable mutation", "docs preserve human authorization boundary"))

    failed = [check for check in checks if check.get("status") != "pass"]
    packet = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "pass" if not failed else "fail",
        "generated_utc": _utc(),
        "root": str(root),
        "checks": checks,
        "failed_checks": failed,
        "allowed_repair_lanes": phi_gate_supervisor.ALLOWED_REPAIR_LANES,
        "authority_boundary": phi_gate_supervisor.AUTHORITY_BOUNDARY,
        "read_surfaces": [path.as_posix() for path in REQUIRED_PATHS],
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            REPORT_VERSIONED.as_posix(),
            "reports/nexus_phi_gate_supervisor_latest.json",
            "reports/nexus_phi_gate_supervisor.v1.1.1.json",
        ],
        "next_action": "Run .\\scripts\\nexus.ps1 phi-gate -Gate ci-core, then .\\scripts\\nexus.ps1 evolve." if not failed else "Repair failed Phi Gate Supervisor compiler checks.",
        "claim_boundary": "Phi Gate Supervisor compilation is local development evidence only. It does not prove correctness, safety, security, production readiness, model understanding, or autonomous authority.",
    }
    return packet


def write_report(root: Path, packet: dict[str, Any]) -> None:
    for path in [REPORT_LATEST, REPORT_VERSIONED]:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS Phi Gate Supervisor contract")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    packet = compile_report(root)
    write_report(root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS Phi Gate Supervisor compiler: {packet['status']}")
    return 0 if packet["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
