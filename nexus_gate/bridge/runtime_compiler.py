from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.bridge.runtime import BoundedBridgeRuntime, demo_events


@dataclass
class RuntimeCompileReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = "Runtime compile report is local development evidence only."


def check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"check": name, "status": "pass" if passed else "fail", "evidence": evidence}


def compile_bounded_runtime(root: str | Path) -> RuntimeCompileReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    required_paths = [
        "docs/bridge/BOUNDED_BRIDGE_RUNTIME.md",
        "state/bounded_bridge_runtime_index.v0.2.0.json",
        "nexus_gate/bridge/runtime.py",
        "nexus_gate/bridge/runtime_compiler.py",
        "scripts/nexus_runtime.ps1",
        "scripts/nexus_runtime.sh",
    ]
    missing = [rel for rel in required_paths if not (root / rel).exists()]
    checks.append(check("runtime_required_paths", not missing, {"missing": missing}))

    runtime = BoundedBridgeRuntime(max_events=3)
    report = runtime.run_batch(demo_events(), runtime_id="compile-demo-runtime")
    runtime.write_report(report, root / "reports")

    counts = report.summary_counts
    checks.append(check(
        "runtime_summary_counts",
        counts.get("engage") == 1 and counts.get("shadow") == 1 and counts.get("reject") == 1,
        {"summary_counts": counts, "status": report.status},
    ))

    checks.append(check(
        "runtime_bound_enforced",
        report.processed_count <= report.max_events and report.truncated_count == 0,
        {"processed_count": report.processed_count, "max_events": report.max_events, "truncated_count": report.truncated_count},
    ))

    bounded = BoundedBridgeRuntime(max_events=2)
    bounded_report = bounded.run_batch(demo_events(), runtime_id="compile-bounded-runtime")
    checks.append(check(
        "runtime_truncates_over_limit",
        bounded_report.status == "bounded" and bounded_report.processed_count == 2 and bounded_report.truncated_count == 1,
        {"status": bounded_report.status, "processed_count": bounded_report.processed_count, "truncated_count": bounded_report.truncated_count},
    ))

    docs = ""
    for rel in ["docs/bridge/BOUNDED_BRIDGE_RUNTIME.md"]:
        path = root / rel
        if path.exists():
            docs += path.read_text(encoding="utf-8", errors="ignore")
    required_markers = ["BoundedRuntimeReport", "No runtime without event limit.", "BridgeSessionReport"]
    missing_markers = [marker for marker in required_markers if marker not in docs]
    checks.append(check("runtime_docs_markers", not missing_markers, {"missing": missing_markers}))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return RuntimeCompileReport(
        system="NEXUS GATE",
        version="0.2.0-runtime-compiler",
        root=str(root),
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE bounded runtime compiler")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = compile_bounded_runtime(args.root)
    reports = Path(args.root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_runtime_compile_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE runtime compile status: {report.status}")

    if report.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
