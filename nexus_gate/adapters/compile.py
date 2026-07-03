from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.adapters.registry import AdapterRegistry, load_manifest
from nexus_gate.runtime.router import NexusRouter


@dataclass
class AdapterCompileReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = "Adapter compile report is local development evidence only."


def check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "check": name,
        "status": "pass" if passed else "fail",
        "evidence": evidence,
    }


def compile_adapter_registry(root: str | Path) -> AdapterCompileReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    required_paths = [
        "docs/adapters/ADAPTER_REGISTRY.md",
        "docs/adapters/LOCAL_DEMO_ADAPTER.md",
        "schemas/adapter_manifest.v0.1.7.schema.json",
        "registry/adapters.local_demo.v0.1.7.json",
        "state/adapter_registry_index.v0.1.7.json",
        "nexus_gate/adapters/registry.py",
        "nexus_gate/adapters/local_demo.py",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(check("adapter_required_paths", not missing, {"missing": missing}))

    registry = AdapterRegistry()
    try:
        manifest = load_manifest(root / "registry/adapters.local_demo.v0.1.7.json")
        entry = registry.register(manifest)
        checks.append(check("adapter_manifest_registers", True, {"adapter_id": entry.manifest.adapter_id}))
    except Exception as exc:
        checks.append(check("adapter_manifest_registers", False, {"error": str(exc)}))
        manifest = None

    adapter = LocalDemoAdapter()
    packet = adapter.normalize_event({
        "packet_id": "adapter-compile-packet",
        "event_type": "demo.message",
        "message": "adapter compile smoke",
        "requested_action": "read_only_signal",
    })
    decision = NexusRouter().route(packet)
    checks.append(check(
        "adapter_statepacket_routes",
        decision.mode == "engage",
        {"packet_id": packet.packet_id, "decision": decision.mode, "reason": decision.reason},
    ))

    receptors = adapter.export_receptors()
    checks.append(check(
        "adapter_exports_receptors",
        bool(receptors) and receptors[0].get("receptor_id") == "local.demo.readonly",
        {"receptors": receptors},
    ))

    docs = ""
    for rel in ["docs/adapters/ADAPTER_REGISTRY.md", "docs/adapters/LOCAL_DEMO_ADAPTER.md"]:
        path = root / rel
        if path.exists():
            docs += path.read_text(encoding="utf-8", errors="ignore")
    required_markers = ["No adapter, no bridge.", "LocalDemoAdapter", "StatePacket"]
    missing_markers = [marker for marker in required_markers if marker not in docs]
    checks.append(check("adapter_docs_markers", not missing_markers, {"missing": missing_markers}))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return AdapterCompileReport(
        system="NEXUS GATE",
        version="0.1.7-adapter-compiler",
        root=str(root),
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE adapter compiler")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = compile_adapter_registry(args.root)
    reports = Path(args.root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_adapter_compile_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE adapter compile status: {report.status}")

    if report.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
