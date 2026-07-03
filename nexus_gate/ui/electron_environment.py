from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


@dataclass
class ElectronEnvironmentReport:
    system: str
    version: str
    root: str
    status: str
    readiness: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    command: str = ".\\scripts\\nexus.ps1 electron-env"
    next_action: str = ""
    claim_boundary: str = (
        "Electron environment readiness is local evidence only. It does not install "
        "dependencies, launch Electron, package an EXE, grant shell authority, or "
        "authorize autonomous action."
    )


def _check(name: str, status: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if status not in {"pass", "warn", "fail"}:
        raise ValueError(f"invalid check status: {status}")
    return {"check": name, "status": status, "evidence": evidence}


def _tool_version(executable: str) -> tuple[str | None, str | None]:
    path = shutil.which(executable)
    if not path:
        return None, None
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return path, f"unreadable: {exc}"
    version = (result.stdout or result.stderr).strip()
    return path, version or "unknown"


def compile_electron_environment(root: str | Path) -> ElectronEnvironmentReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    package_path = root / "electron" / "package.json"
    if not package_path.exists():
        checks.append(_check("electron_package_present", "fail", {"path": "electron/package.json"}))
        package: dict[str, Any] = {}
    else:
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
            checks.append(_check("electron_package_present", "pass", {"path": "electron/package.json"}))
        except json.JSONDecodeError as exc:
            package = {}
            checks.append(_check("electron_package_valid_json", "fail", {"error": str(exc)}))

    declared = "electron" in package.get("devDependencies", {})
    checks.append(_check(
        "electron_dependency_declared",
        "pass" if declared else "fail",
        {"devDependencies": package.get("devDependencies", {})},
    ))

    for tool in ["node", "npm"]:
        path, version = _tool_version(tool)
        checks.append(_check(
            f"{tool}_available",
            "pass" if path else "warn",
            {"path": path, "version": version},
        ))

    module_path = root / "electron" / "node_modules" / "electron"
    checks.append(_check(
        "electron_node_module_present",
        "pass" if module_path.exists() else "warn",
        {
            "path": "electron/node_modules/electron",
            "install_command": "cd electron; npm install",
            "mutation_performed": False,
        },
    ))

    failed = [item for item in checks if item["status"] == "fail"]
    warned = [item for item in checks if item["status"] == "warn"]
    status = "fail" if failed else "pass"
    readiness = "blocked" if failed else ("ready" if not warned else "not_ready")
    if failed:
        next_action = "Repair failing Electron scaffold metadata, then rerun .\\scripts\\nexus.ps1 electron-env."
    elif warned:
        next_action = (
            "Electron runtime is not ready yet. After explicit operator authorization, "
            "install dependencies in electron/ and rerun this gate."
        )
    else:
        next_action = "Electron runtime prerequisites are present. Next safe step is a governed smoke runner."

    return ElectronEnvironmentReport(
        system="NEXUS GATE",
        version="0.3.5-electron-environment",
        root=str(root),
        status=status,
        readiness=readiness,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        next_action=next_action,
    )


def write_electron_environment_report(report: ElectronEnvironmentReport, root: str | Path) -> Path:
    reports = Path(root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_electron_environment_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return latest
