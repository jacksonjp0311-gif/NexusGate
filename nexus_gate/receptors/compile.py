from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.receptors.compatibility import evaluate_compatibility
from nexus_gate.receptors.registry import ReceptorRegistry, load_receptor_manifests


@dataclass
class ReceptorCompileReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = "Receptor compile report is local development evidence only."


def check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"check": name, "status": "pass" if passed else "fail", "evidence": evidence}


def compile_receptor_registry(root: str | Path) -> ReceptorCompileReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []
    required_paths = [
        "docs/receptors/RECEPTOR_REGISTRY.md",
        "docs/receptors/LOCAL_DEMO_RECEPTORS.md",
        "schemas/receptor_manifest.v0.1.8.schema.json",
        "registry/receptors.local_demo.v0.1.8.json",
        "state/receptor_registry_index.v0.1.8.json",
        "nexus_gate/receptors/registry.py",
        "nexus_gate/receptors/compatibility.py",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(check("receptor_required_paths", not missing, {"missing": missing}))

    registry = ReceptorRegistry()
    try:
        manifests = load_receptor_manifests(root / "registry/receptors.local_demo.v0.1.8.json")
        entries = [registry.register(manifest) for manifest in manifests]
        checks.append(check("receptor_manifests_register", True, {"receptors": [entry.manifest.receptor_id for entry in entries]}))
    except Exception as exc:
        checks.append(check("receptor_manifests_register", False, {"error": str(exc)}))
        manifests = []

    adapter = LocalDemoAdapter()
    readonly_packet = adapter.normalize_event({"packet_id": "receptor-readonly-packet", "requested_action": "read_only_signal"})
    tool_packet = adapter.normalize_event({"packet_id": "receptor-tool-packet", "requested_action": "tool_call", "authority_scope": []})

    if manifests:
        readonly = next((item for item in manifests if item.receptor_id == "local.demo.readonly"), manifests[0])
        tool = next((item for item in manifests if item.receptor_id == "local.demo.tool_shadow"), manifests[-1])
        readonly_decision = evaluate_compatibility(readonly_packet, readonly)
        tool_decision = evaluate_compatibility(tool_packet, tool)
        checks.append(check("readonly_receptor_compatible", readonly_decision.mode == "compatible", readonly_decision.to_dict()))
        checks.append(check("tool_receptor_shadows_without_authority", tool_decision.mode == "shadow", tool_decision.to_dict()))

    docs = ""
    for rel in ["docs/receptors/RECEPTOR_REGISTRY.md", "docs/receptors/LOCAL_DEMO_RECEPTORS.md"]:
        path = root / rel
        if path.exists():
            docs += path.read_text(encoding="utf-8", errors="ignore")
    required_markers = ["No receptor, no transfer target.", "CompatibilityDecision", "local.demo.readonly"]
    missing_markers = [marker for marker in required_markers if marker not in docs]
    checks.append(check("receptor_docs_markers", not missing_markers, {"missing": missing_markers}))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return ReceptorCompileReport("NEXUS GATE", "0.1.8-receptor-compiler", str(root), status, datetime.now(timezone.utc).isoformat(), checks)


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE receptor compiler")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = compile_receptor_registry(args.root)
    reports = Path(args.root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "nexus_receptor_compile_report_latest.json").write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE receptor compile status: {report.status}")
    if report.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
