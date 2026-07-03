from __future__ import annotations

import argparse
import compileall
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.compiler.gates import GateResult
from nexus_gate.core.packets import StatePacket
from nexus_gate.evidence.ledger import JsonlLedger
from nexus_gate.runtime.router import NexusRouter


REQUIRED_PATHS = [
    "README.md",
    "pyproject.toml",
    "nexus_gate/__init__.py",
    "nexus_gate/core/packets.py",
    "nexus_gate/adapters/base.py",
    "nexus_gate/runtime/router.py",
    "nexus_gate/policies/authority.py",
    "schemas/state_packet.v0.1.0.schema.json",
    "schemas/framework_adapter.v0.1.0.schema.json",
    "registry/nexus_gate_manifest.v0.1.0.json",
    "state/nexus_gate_state.v0.1.0.json",
    "ledger/nexus_gate_ledger.v0.1.0.jsonl",
]

REQUIRED_RUNTIME_LAWS = [
    "No adapter, no bridge.",
    "No schema, no route.",
    "No authority verification, no mutation.",
    "No replay certificate, no memory promotion.",
    "No wound route, no retrust.",
    "No ledger stub, no compounding.",
]

FORBIDDEN_BYPASS_MARKERS = [
    "bypass_authority=True",
    "skip_authority_gate=True",
    "disable_ledger=True",
    "unsafe_engage=True",
    "allow_mutation_without_authority",
]


@dataclass
class CompileReport:
    """Gated compiler output.

    A pass means the local scaffold satisfies the current development gates.
    It is not a security proof, correctness proof, or production validation.
    """

    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    duration_ms: int
    gates: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = (
        "Local development gate only. Not a production validation, safety proof, "
        "security proof, or correctness proof."
    )


class NexusCompiler:
    """Local gated compiler for NEXUS GATE development.

    The compiler does not compile a programming language into machine code.
    It compiles repository state into a pass/fail promotion decision.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.gates: list[GateResult] = []

    def add(self, gate: str, status: str, message: str, evidence: dict[str, Any] | None = None) -> None:
        self.gates.append(GateResult(gate=gate, status=status, message=message, evidence=evidence or {}))

    def gate_root_exists(self) -> None:
        if self.root.exists() and self.root.is_dir():
            self.add("root_anchor", "pass", "Project root exists.", {"root": str(self.root)})
            return
        self.add("root_anchor", "fail", "Project root is missing.", {"root": str(self.root)})

    def gate_required_paths(self) -> None:
        missing = []
        for rel in REQUIRED_PATHS:
            path = self.root / rel
            if not path.exists():
                missing.append(rel)
        if not missing:
            self.add("required_paths", "pass", "All required paths exist.", {"count": len(REQUIRED_PATHS)})
            return
        self.add("required_paths", "fail", "Required paths are missing.", {"missing": missing})

    def gate_manifest_runtime_laws(self) -> None:
        manifest_path = self.root / "registry" / "nexus_gate_manifest.v0.1.0.json"
        if not manifest_path.exists():
            self.add("runtime_laws", "fail", "Manifest missing.", {"path": str(manifest_path)})
            return

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("runtime_laws", "fail", "Manifest JSON failed to parse.", {"error": str(exc)})
            return

        laws = data.get("runtime_laws", [])
        missing = [law for law in REQUIRED_RUNTIME_LAWS if law not in laws]

        if not missing:
            self.add("runtime_laws", "pass", "Required runtime laws are present.", {"required": REQUIRED_RUNTIME_LAWS})
            return

        self.add("runtime_laws", "fail", "Required runtime laws are missing.", {"missing": missing})

    def gate_json_files_parse(self) -> None:
        json_files = list(self.root.glob("schemas/*.json")) + list(self.root.glob("registry/*.json")) + list(self.root.glob("state/*.json"))
        failures = []

        for path in json_files:
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                failures.append({"path": str(path.relative_to(self.root)), "error": str(exc)})

        if not failures:
            self.add("json_parse", "pass", "Schema, registry, and state JSON files parse.", {"count": len(json_files)})
            return

        self.add("json_parse", "fail", "One or more JSON files failed to parse.", {"failures": failures})

    def gate_forbidden_bypass_markers(self) -> None:
        findings = []
        scan_roots = [self.root / "nexus_gate", self.root / "scripts", self.root / "tests"]

        for scan_root in scan_roots:
            if not scan_root.exists():
                continue
            for path in scan_root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in {".py", ".ps1", ".md", ".json", ".toml"}:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for marker in FORBIDDEN_BYPASS_MARKERS:
                    if marker in text:
                        findings.append({
                            "path": str(path.relative_to(self.root)),
                            "marker": marker,
                        })

        if not findings:
            self.add("forbidden_bypass_scan", "pass", "No forbidden bypass markers found.", {"markers": FORBIDDEN_BYPASS_MARKERS})
            return

        self.add("forbidden_bypass_scan", "fail", "Forbidden bypass markers found.", {"findings": findings})

    def gate_python_compile(self) -> None:
        ok = compileall.compile_dir(str(self.root / "nexus_gate"), quiet=1)
        tests_ok = compileall.compile_dir(str(self.root / "tests"), quiet=1)

        if ok and tests_ok:
            self.add("python_compile", "pass", "Python source compiled.", {"paths": ["nexus_gate", "tests"]})
            return

        self.add("python_compile", "fail", "Python compile failed.", {"paths": ["nexus_gate", "tests"]})

    def gate_unit_tests(self) -> None:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
        proc = subprocess.run(
            cmd,
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=120,
        )

        evidence = {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }

        if proc.returncode == 0:
            self.add("unit_tests", "pass", "Unit tests passed.", evidence)
            return

        self.add("unit_tests", "fail", "Unit tests failed.", evidence)

    def gate_route_contracts(self) -> None:
        router = NexusRouter()

        missing_schema = StatePacket(
            packet_id="compiler-missing-schema",
            source_framework="compiler",
            source_surface="gate",
            schema_id="",
            schema_version="0.1.0",
            requested_action="read_only_signal",
            payload={},
        )
        no_authority_tool = StatePacket(
            packet_id="compiler-tool-no-authority",
            source_framework="compiler",
            source_surface="gate",
            schema_id="NEXUS_STATE_PACKET",
            schema_version="0.1.0",
            requested_action="tool_call",
            payload={},
            authority_scope=[],
        )
        read_only = StatePacket(
            packet_id="compiler-read-only",
            source_framework="compiler",
            source_surface="gate",
            schema_id="NEXUS_STATE_PACKET",
            schema_version="0.1.0",
            requested_action="read_only_signal",
            payload={},
            authority_scope=[],
        )

        decisions = {
            "missing_schema": router.route(missing_schema).mode,
            "no_authority_tool": router.route(no_authority_tool).mode,
            "read_only": router.route(read_only).mode,
        }

        expected = {
            "missing_schema": "reject",
            "no_authority_tool": "shadow",
            "read_only": "engage",
        }

        if decisions == expected:
            self.add("route_contracts", "pass", "Core route contracts hold.", {"decisions": decisions})
            return

        self.add("route_contracts", "fail", "Core route contracts violated.", {"decisions": decisions, "expected": expected})

    def gate_ledger_appendable(self) -> None:
        ledger_path = self.root / "ledger" / "nexus_gate_ledger.v0.1.0.jsonl"
        try:
            ledger = JsonlLedger(ledger_path)
            ledger.append({
                "event": "compiler_ledger_gate_probe",
                "version": "0.1.1",
                "status": "probe",
            })
        except Exception as exc:
            self.add("ledger_appendable", "fail", "Ledger append failed.", {"error": str(exc)})
            return

        self.add("ledger_appendable", "pass", "Ledger is appendable.", {"path": str(ledger_path.relative_to(self.root))})

    def run(self) -> CompileReport:
        start = time.perf_counter()

        self.gate_root_exists()
        self.gate_required_paths()
        self.gate_manifest_runtime_laws()
        self.gate_json_files_parse()
        self.gate_forbidden_bypass_markers()
        self.gate_python_compile()
        self.gate_route_contracts()
        self.gate_unit_tests()
        self.gate_ledger_appendable()

        failed = [gate for gate in self.gates if gate.failed]
        status = "pass" if not failed else "fail"

        duration_ms = int((time.perf_counter() - start) * 1000)

        return CompileReport(
            system="NEXUS GATE",
            version="0.1.1-gated-compiler",
            root=str(self.root),
            status=status,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            gates=[asdict(gate) for gate in self.gates],
        )

    def write_report(self, report: CompileReport) -> Path:
        reports_dir = self.root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = reports_dir / f"nexus_compile_report_{stamp}.json"
        path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

        latest = reports_dir / "nexus_compile_report_latest.json"
        latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

        ledger = JsonlLedger(self.root / "ledger" / "nexus_gate_ledger.v0.1.0.jsonl")
        ledger.append({
            "event": "nexus_compile",
            "version": report.version,
            "status": report.status,
            "report_path": str(path.relative_to(self.root)),
            "duration_ms": report.duration_ms,
            "failed_gates": [
                gate["gate"]
                for gate in report.gates
                if gate["status"] == "fail"
            ],
        })

        return path


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-compile", description="NEXUS GATE gated compiler")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    compiler = NexusCompiler(args.root)
    report = compiler.run()
    path = compiler.write_report(report)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    if not args.json:
        print(f"NEXUS GATE compile status: {report.status}")
        print(f"Report: {path}")

    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()