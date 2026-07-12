from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRODUCT_VERSION = "2.0.0"
PRODUCT_PHASE = "Coherence Continuity Protocol"
SCHEMA = "NEXUS_ORIGIN_SEAL.v2.0.0"
REPORT_LATEST = Path("reports") / "nexus_origin_seal_latest.json"
STATE_LATEST = Path("state") / "nexus_origin_manifest_latest.json"

CLAIM_BOUNDARY = (
    "Origin Seal is local development evidence only. It binds current repository "
    "identity, key surface hashes, commit state, and subsystem version lineage. "
    "It does not prove correctness, safety, security, production readiness, "
    "model understanding, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "version_claim_without_manifest",
    "stale_evidence_as_truth",
    "bypass_evolve",
    "git_write",
    "external_api_writes",
    "secret_access",
]

ORIGIN_SURFACES = [
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "nexus_gate/__init__.py",
    "docs/updates/UPDATE_CHART.md",
    "docs/versioning/NEXUS_CHANGELOG.md",
    "docs/versioning/NEXUS_LINEAGE_PROTOCOL.md",
    "state/nexus_lineage_manifest_latest.json",
    "state/algorithms/nexus_algorithm_cards_latest.json",
    "state/discoveries/nexus_discovery_cards_latest.json",
    "reports/nexus_compile_report_latest.json",
    "reports/nexus_meta_orchestrator_gate_latest.json",
    "reports/nexus_predictive_memory_orchestrator_latest.json",
    "reports/nexus_cortex_refresh_report_latest.json",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(_read_text(path))
    except Exception:
        return default


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _surface_record(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        return {"path": rel, "exists": False, "bytes": 0, "sha256": None}
    data = path.read_bytes()
    return {
        "path": rel,
        "exists": True,
        "bytes": len(data),
        "sha256": _sha256_bytes(data),
    }


def _git(root: Path, args: list[str], timeout: int = 10) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception:
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _package_version(root: Path) -> str:
    text = _read_text(root / "pyproject.toml")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else "unknown"


def _module_version(root: Path) -> str:
    text = _read_text(root / "nexus_gate" / "__init__.py")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else "unknown"


def _readme_current_line(root: Path) -> str:
    text = _read_text(root / "README.md")
    match = re.search(r"NEXUS GATE current line:\s*(.+)", text)
    return match.group(1).strip() if match else ""


def _manifest_hash(packet: dict[str, Any]) -> str:
    encoded = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def build_origin_seal(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    surfaces = [_surface_record(root_path, rel) for rel in ORIGIN_SURFACES]
    surface_hash = _sha256_bytes(
        json.dumps(
            [{"path": item["path"], "sha256": item["sha256"]} for item in surfaces],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    commit = _git(root_path, ["rev-parse", "HEAD"]) or "unknown"
    branch = _git(root_path, ["branch", "--show-current"]) or "unknown"
    dirty_entries = [line for line in _git(root_path, ["status", "--short"]).splitlines() if line.strip()]
    lineage = _read_json(root_path / "state" / "nexus_lineage_manifest_latest.json", {})
    compile_report = _read_json(root_path / "reports" / "nexus_compile_report_latest.json", {})
    meta = _read_json(root_path / "reports" / "nexus_meta_orchestrator_gate_latest.json", {})
    predictive_memory = _read_json(root_path / "reports" / "nexus_predictive_memory_orchestrator_latest.json", {})
    cortex_refresh = _read_json(root_path / "reports" / "nexus_cortex_refresh_report_latest.json", {})

    version_line = _readme_current_line(root_path)
    product_line_ok = f"v{PRODUCT_VERSION}" in version_line and PRODUCT_PHASE in version_line
    required_surfaces = [
        "README.md",
        "AGENTS.md",
        "pyproject.toml",
        "nexus_gate/__init__.py",
        "state/algorithms/nexus_algorithm_cards_latest.json",
        "state/discoveries/nexus_discovery_cards_latest.json",
    ]
    surface_map = {item["path"]: item for item in surfaces}
    required_present = all(surface_map[rel]["exists"] for rel in required_surfaces)
    compile_visible = bool(compile_report)
    meta_visible = bool(meta)
    memory_visible = bool(predictive_memory)

    checks = {
        "product_line_current": product_line_ok,
        "required_origin_surfaces_present": required_present,
        "compile_report_visible": compile_visible,
        "meta_orchestrator_visible": meta_visible,
        "predictive_memory_visible": memory_visible,
        "authority_boundary_declared": True,
        "final_evolve_required": True,
    }
    legacy_version_lineage = {
        "product_version": PRODUCT_VERSION,
        "product_phase": PRODUCT_PHASE,
        "pyproject_distribution_version": _package_version(root_path),
        "python_package_api_version": _module_version(root_path),
        "lineage_manifest_system_version": lineage.get("system_version"),
        "lineage_manifest_phase": lineage.get("active_phase"),
        "meta_orchestrator_version": meta.get("version"),
        "predictive_memory_version": predictive_memory.get("version"),
        "cortex_refresh_version": cortex_refresh.get("version"),
    }
    packet = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "product_version": PRODUCT_VERSION,
        "product_phase": PRODUCT_PHASE,
        "status": "pass" if all(checks.values()) else "warn",
        "generated_utc": _utc(),
        "branch": branch,
        "commit": commit,
        "dirty_count": len(dirty_entries),
        "dirty_entries_sample": dirty_entries[:40],
        "surface_hash": surface_hash,
        "origin_surfaces": surfaces,
        "legacy_version_lineage": legacy_version_lineage,
        "checks": checks,
        "readme_current_line": version_line,
        "read_surfaces": ORIGIN_SURFACES,
        "write_surfaces": [REPORT_LATEST.as_posix(), STATE_LATEST.as_posix()],
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "autonomous_authority": False,
            "repo_mutation": False,
            "git_write": False,
            "external_api_writes": False,
            "secret_access": False,
            "human_authorization_required_for_mutation": True,
            "final_evolve_required_before_commit": True,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    packet["origin_manifest_hash"] = _manifest_hash(packet)
    packet["next_action"] = ".\\scripts\\nexus.ps1 predictive-memory; .\\scripts\\nexus.ps1 evolve"
    return packet


def write_origin_seal(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    for rel in (REPORT_LATEST, STATE_LATEST):
        path = root_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "NEXUS ORIGIN SEAL",
            f"Version: v{packet.get('product_version')} {packet.get('product_phase')}",
            f"Status: {packet.get('status')}",
            f"Commit: {packet.get('commit')}",
            f"Dirty entries: {packet.get('dirty_count')}",
            f"Manifest hash: {packet.get('origin_manifest_hash')}",
            f"Next: {packet.get('next_action')}",
            "Boundary: origin evidence only; human authority and final evolve still control durable mutation.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the NEXUS current origin seal.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = build_origin_seal(args.root)
    write_origin_seal(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
