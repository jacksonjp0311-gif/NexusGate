from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


EXPECTED_ALLOWLIST = {
    "evolve",
    "interface",
    "feedback",
    "heal",
    "status",
    "compact",
    "interconnect",
    "runtime",
    "pack",
}

EXPECTED_BLOCKED = {
    "arbitrary_shell_commands",
    "external_api_write",
    "secret_access",
    "self_authorize",
    "memory_promotion_without_evidence",
    "ungated_repo_mutation",
    "mutate_graph_state",
    "bypass_evolve",
}


@dataclass
class ElectronPreflightReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    read_surfaces: list[str] = field(default_factory=list)
    allowlisted_commands: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    claim_boundary: str = (
        "Electron preflight is local HUD runtime evidence only. It validates bounded presentation "
        "surfaces, package metadata, smoke hooks, and governance markers. It does not package a "
        "desktop app, validate production readiness, grant shell authority, or authorize autonomous action."
    )


def _check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"check": name, "status": "pass" if passed else "fail", "evidence": evidence}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_electron_preflight(root: str | Path) -> ElectronPreflightReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    required_paths = [
        "docs/ui/ELECTRON_READ_CONTRACT.md",
        "docs/ui/ELECTRON_HUD_RUNTIME.md",
        "docs/ui/ELECTRON_SHELL_SCAFFOLD.md",
        "docs/intelligence/REFLECTIVE_INTELLIGENCE_LOOP.md",
        "docs/interfaces/INTERFACE_ADAPTER_CONTRACT.md",
        "docs/versioning/NEXUS_LINEAGE_PROTOCOL.md",
        "electron/README.md",
        "electron/package.json",
        "electron/package-lock.json",
        "electron/main.js",
        "electron/preload.js",
        "electron/renderer/index.html",
        "electron/renderer/renderer.js",
        "electron/renderer/styles.css",
        "state/electron_read_contract_index.v0.3.2.json",
        "state/electron_shell_scaffold_index.v0.3.3.json",
        "state/electron_hud_runtime_index.v0.3.6.json",
        "state/interface_adapter_contract_index.v0.3.7.json",
        "state/nexus_lineage_manifest_latest.json",
        "tests/test_electron_hud_runtime.py",
        "tests/test_reflective_intelligence_loop.py",
        "tests/test_electron_read_contract.py",
        "tests/test_electron_shell_scaffold.py",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(_check("electron_required_paths", not missing, {"missing": missing}))

    contract = _load_json(root / "state/electron_read_contract_index.v0.3.2.json")
    scaffold = _load_json(root / "state/electron_shell_scaffold_index.v0.3.3.json")
    package = _load_json(root / "electron/package.json")

    read_surfaces = list(contract.get("read_surfaces", []))
    allowlisted = set(contract.get("allowlisted_commands", []))
    scaffold_allowlisted = set(scaffold.get("allowlisted_commands", []))
    blocked = set(contract.get("blocked_actions", [])) | set(scaffold.get("blocked_actions", []))

    checks.append(_check(
        "electron_allowlist_matches_contract",
        allowlisted == EXPECTED_ALLOWLIST and scaffold_allowlisted == EXPECTED_ALLOWLIST,
        {
            "contract_allowlist": sorted(allowlisted),
            "scaffold_allowlist": sorted(scaffold_allowlisted),
            "expected": sorted(EXPECTED_ALLOWLIST),
        },
    ))

    checks.append(_check(
        "electron_blocked_actions_complete",
        EXPECTED_BLOCKED.issubset(blocked),
        {"missing": sorted(EXPECTED_BLOCKED - blocked)},
    ))

    checks.append(_check(
        "electron_required_surface_pair",
        "reports/tui/nexus_tui_snapshot_latest.html" in read_surfaces
        and "reports/tui/nexus_tui_surface_latest.json" in read_surfaces,
        {"read_surfaces": read_surfaces},
    ))

    required_reflective_surfaces = {
        "reports/nexus_reflective_loop_report_latest.json",
        "state/nexus_lineage_manifest_latest.json",
        "state/interface_adapter_contract_index.v0.3.7.json",
    }
    checks.append(_check(
        "electron_reflective_surfaces_declared",
        required_reflective_surfaces.issubset(set(read_surfaces)),
        {"missing": sorted(required_reflective_surfaces - set(read_surfaces))},
    ))

    main_js = (root / "electron/main.js").read_text(encoding="utf-8")
    preload_js = (root / "electron/preload.js").read_text(encoding="utf-8")
    renderer_html = (root / "electron/renderer/index.html").read_text(encoding="utf-8")
    renderer_js = (root / "electron/renderer/renderer.js").read_text(encoding="utf-8")

    required_main_markers = [
        "contextIsolation: true",
        "nodeIntegration: false",
        "sandbox: true",
        "shell: false",
        "ALLOWLISTED_COMMANDS",
        "READ_SURFACES",
        "scripts\", \"nexus.ps1",
        "nexus_electron_smoke_report_latest.json",
        "nexus_reflective_loop_report_latest.json",
        "nexus_lineage_manifest_latest.json",
        "--smoke",
        "disableHardwareAcceleration",
        "nexus:surfaceExists",
    ]
    missing_main_markers = [marker for marker in required_main_markers if marker not in main_js]
    forbidden_main_markers = ["exec(", "execFile(", "shell: true"]
    present_forbidden_main = [marker for marker in forbidden_main_markers if marker in main_js]
    checks.append(_check(
        "electron_main_security_markers",
        not missing_main_markers and not present_forbidden_main,
        {"missing": missing_main_markers, "forbidden_present": present_forbidden_main},
    ))

    checks.append(_check(
        "electron_preload_api_limited",
        'contextBridge.exposeInMainWorld("nexus"' in preload_js
        and "readSurface" in preload_js
        and "runLane" in preload_js
        and "getContract" in preload_js
        and "surfaceExists" in preload_js
        and "child_process" not in preload_js
        and 'require("fs")' not in preload_js,
        {"preload_api": "nexus"},
    ))

    checks.append(_check(
        "electron_renderer_uses_preload_bridge",
        "window.nexus.readSurface" in renderer_js
        and "window.nexus.runLane" in renderer_js
        and "window.nexus.getContract" in renderer_js,
        {"renderer_bridge": "window.nexus"},
    ))

    checks.append(_check(
        "electron_renderer_hud_title",
        "<title>NEXUS GATE</title>" in renderer_html
        and "<h1>NEXUS GATE</h1>" in renderer_html
        and "Hermes" not in renderer_html
        and "Process Lanes" in renderer_html
        and "Feedback Summary" in renderer_html
        and "AI Handoff Package" in renderer_html,
        {"title": "NEXUS GATE"},
    ))

    checks.append(_check(
        "electron_package_private",
        package.get("private") is True
        and package.get("main") == "main.js"
        and package.get("scripts", {}).get("smoke") == "electron . --smoke"
        and package.get("scripts", {}).get("start") == "electron .",
        {
            "private": package.get("private"),
            "main": package.get("main"),
            "scripts": package.get("scripts", {}),
        },
    ))

    boundary_text = " ".join([
        str(contract.get("claim_boundary", "")),
        str(scaffold.get("claim_boundary", "")),
    ])
    checks.append(_check(
        "electron_claim_boundary_present",
        ("local development evidence" in boundary_text or "local installed Electron runtime" in boundary_text)
        and "shell authority" in boundary_text
        and "autonomous" in boundary_text,
        {"boundary": boundary_text},
    ))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return ElectronPreflightReport(
        system="NEXUS GATE",
        version="0.3.6-electron-hud-runtime-preflight",
        root=str(root),
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        read_surfaces=read_surfaces,
        allowlisted_commands=sorted(allowlisted),
        blocked_actions=sorted(blocked),
    )


def write_electron_preflight_report(report: ElectronPreflightReport, root: str | Path) -> Path:
    reports = Path(root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_electron_preflight_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return latest
