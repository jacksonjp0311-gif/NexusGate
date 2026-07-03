from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.bridge.session import BridgeSessionRunner


@dataclass
class BridgeCompileReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = "Bridge compile report is local development evidence only."


def check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"check": name, "status": "pass" if passed else "fail", "evidence": evidence}


def compile_bridge_session(root: str | Path) -> BridgeCompileReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    required_paths = [
        "docs/bridge/BRIDGE_SESSION_RUNNER.md",
        "state/bridge_session_index.v0.1.9.json",
        "nexus_gate/bridge/session.py",
        "nexus_gate/bridge/compile.py",
        "scripts/nexus_bridge_demo.ps1",
        "scripts/nexus_bridge_demo.sh",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(check("bridge_required_paths", not missing, {"missing": missing}))

    runner = BridgeSessionRunner(root / "registry/receptors.local_demo.v0.1.8.json")

    readonly = runner.run({
        "session_id": "bridge-compile-readonly",
        "packet_id": "bridge-readonly",
        "event_type": "demo.message",
        "message": "bridge compile readonly",
        "requested_action": "read_only_signal",
    })
    checks.append(check(
        "bridge_readonly_engages",
        readonly.final_mode == "engage",
        readonly.to_dict(),
    ))

    tool_shadow = runner.run({
        "session_id": "bridge-compile-tool",
        "packet_id": "bridge-tool",
        "event_type": "demo.tool_request",
        "requested_action": "tool_call",
        "authority_scope": [],
    })
    checks.append(check(
        "bridge_tool_call_shadows_without_authority",
        tool_shadow.final_mode == "shadow",
        tool_shadow.to_dict(),
    ))

    unsupported_schema = runner.run({
        "session_id": "bridge-compile-bad-schema",
        "packet_id": "bridge-bad-schema",
        "event_type": "demo.message",
        "schema_id": "UNKNOWN_SCHEMA",
        "requested_action": "read_only_signal",
    })
    checks.append(check(
        "bridge_unsupported_schema_rejects",
        unsupported_schema.final_mode == "reject",
        unsupported_schema.to_dict(),
    ))

    docs = ""
    for rel in ["docs/bridge/BRIDGE_SESSION_RUNNER.md"]:
        path = root / rel
        if path.exists():
            docs += path.read_text(encoding="utf-8", errors="ignore")
    required_markers = ["BridgeSessionReport", "No bridge session without adapter normalization.", "CompatibilityDecision"]
    missing_markers = [marker for marker in required_markers if marker not in docs]
    checks.append(check("bridge_docs_markers", not missing_markers, {"missing": missing_markers}))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return BridgeCompileReport(
        system="NEXUS GATE",
        version="0.1.9-bridge-compiler",
        root=str(root),
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE bridge compiler")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = compile_bridge_session(args.root)
    reports = Path(args.root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_bridge_compile_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE bridge compile status: {report.status}")

    if report.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
