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
    "README_90_SECONDS.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "ROADMAP.md",
    "pyproject.toml",
    "nexus_gate/__init__.py",
    "nexus_gate/core/packets.py",
    "nexus_gate/adapters/base.py",
    "nexus_gate/runtime/router.py",
    "nexus_gate/policies/authority.py",
    "nexus_gate/evidence/failure_modes.py",
    "schemas/state_packet.v0.1.3.schema.json",
    "schemas/failure_mode.v0.1.3.schema.json",
    "registry/nexus_gate_manifest.v0.1.3.json",
    "state/nexus_gate_state.v0.1.3.json",
    "ledger/nexus_gate_ledger.v0.1.0.jsonl",
    "docs/context/repository_context_index.json",
    "docs/context/rcc_nexus_index.json",
    "docs/context/validation_surface.md",
    "docs/failure_modes/FAILURE_MODES.md",
    "docs/runtime/GATED_RUNTIME_LOOP.md",
    "docs/runtime/RELEASE_GATES.md",
    "docs/runtime/CROSS_PLATFORM_COMMANDS.md",
    "rcc/nexus/README.md",
    "rcc/nexus/route_map.json",
    "rcc/nexus/task_routing_matrix.md",
    "rcc/nexus/echo_location_template.md",
    "rcc/nexus/agent_handoff_contract.md",
    "scripts/nexus_compile.ps1",
    "scripts/nexus_once.ps1",
    "scripts/nexus_dev_loop.ps1",
    "scripts/nexus_promote.ps1",
    "scripts/nexus_compile.sh",
    "scripts/nexus_once.sh",
    "scripts/nexus_dev_loop.sh",
    "scripts/nexus_promote.sh",
]

MINI_README_DIRS = [
    "nexus_gate",
    "nexus_gate/core",
    "nexus_gate/runtime",
    "nexus_gate/compiler",
    "nexus_gate/evidence",
    "docs",
    "docs/context",
    "docs/failure_modes",
    "rcc/nexus",
    "scripts",
    "tests",
    "state",
    "ledger",
    "reports",
    "logs",
]

REQUIRED_README_MARKERS = [
    "PART I - Human README",
    "PART II - RHP Nexus README",
    "PART III - AI Agent README",
    "Human Director Box",
    "RHP Origin Alignment",
    "AI Operating Contract",
    "Failure Modes",
    "No RHP alignment, no durable mutation.",
    "No mini README, no blind patching.",
]

REQUIRED_RUNTIME_LAWS = [
    "No adapter, no bridge.",
    "No schema, no route.",
    "No authority verification, no mutation.",
    "No replay certificate, no memory promotion.",
    "No wound route, no retrust.",
    "No ledger stub, no compounding.",
]

MUST_CALL_COMPILER_DIRECTLY = [
    "scripts/nexus_compile.ps1",
    "scripts/nexus_once.ps1",
    "scripts/nexus_dev_loop.ps1",
    "scripts/nexus_promote.ps1",
    "scripts/nexus_compile.sh",
    "scripts/nexus_once.sh",
    "scripts/nexus_dev_loop.sh",
    "scripts/nexus_promote.sh",
]

FORBIDDEN_BYPASS_MARKERS = [
    "bypass_" + "authority=True",
    "skip_" + "authority_gate=True",
    "disable_" + "ledger=True",
    "unsafe_" + "engage=True",
    "allow_" + "mutation_without_authority",
]

SCAN_SUFFIXES = {".py", ".ps1", ".sh", ".md", ".json", ".toml", ".yml", ".yaml"}
EXCLUDED_SCAN_PATHS = {"nexus_gate/compiler/compiler.py"}


@dataclass
class CompileReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    duration_ms: int
    gates: list[dict[str, Any]] = field(default_factory=list)
    claim_boundary: str = "Local development gate only. Not a production validation, safety proof, security proof, or correctness proof."


class NexusCompiler:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.gates: list[GateResult] = []

    def add(self, gate: str, status: str, message: str, evidence: dict[str, Any] | None = None) -> None:
        self.gates.append(GateResult(gate=gate, status=status, message=message, evidence=evidence or {}))

    def gate_required_paths(self) -> None:
        missing = [rel for rel in REQUIRED_PATHS if not (self.root / rel).exists()]
        if missing:
            self.add("required_paths", "fail", "Required paths are missing.", {"missing": missing})
            return
        self.add("required_paths", "pass", "All required paths exist.", {"count": len(REQUIRED_PATHS)})

    def gate_readme_trisection(self) -> None:
        path = self.root / "README.md"
        if not path.exists():
            self.add("readme_trisection", "fail", "README.md is missing.", {})
            return
        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = [m for m in REQUIRED_README_MARKERS if m not in text]
        if missing:
            self.add("readme_trisection", "fail", "README missing required Human/RHP Nexus/AI markers.", {"missing": missing})
            return
        self.add("readme_trisection", "pass", "README contains Human/RHP Nexus/AI trisection.", {"markers": REQUIRED_README_MARKERS})

    def gate_manifest_runtime_laws(self) -> None:
        manifest_path = self.root / "registry" / "nexus_gate_manifest.v0.1.3.json"
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
        if missing:
            self.add("runtime_laws", "fail", "Required runtime laws are missing.", {"missing": missing})
            return
        self.add("runtime_laws", "pass", "Required runtime laws are present.", {"required": REQUIRED_RUNTIME_LAWS})

    def gate_json_files_parse(self) -> None:
        json_files = list(self.root.glob("schemas/*.json")) + list(self.root.glob("registry/*.json")) + list(self.root.glob("state/*.json")) + list((self.root / "docs/context").glob("*.json")) + list((self.root / "rcc/nexus").glob("*.json"))
        failures = []
        for path in json_files:
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                failures.append({"path": str(path.relative_to(self.root)), "error": str(exc)})
        if failures:
            self.add("json_parse", "fail", "One or more JSON files failed to parse.", {"failures": failures})
            return
        self.add("json_parse", "pass", "Schema, registry, state, context, and route JSON files parse.", {"count": len(json_files)})

    def gate_mini_readmes(self) -> None:
        missing = []
        bad = []
        for rel in MINI_README_DIRS:
            path = self.root / rel / "README.md"
            if not path.exists():
                missing.append(str(path.relative_to(self.root)))
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "RCC Nexus Echo Location" not in text:
                bad.append(str(path.relative_to(self.root)))
        if missing or bad:
            self.add("mini_readmes", "fail", "Mini README coverage failed.", {"missing": missing, "missing_echo_location": bad})
            return
        self.add("mini_readmes", "pass", "Mini README Echo Location coverage passed.", {"count": len(MINI_README_DIRS)})

    def gate_failure_modes(self) -> None:
        path = self.root / "docs/failure_modes/FAILURE_MODES.md"
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        required = ["schema_missing", "authority_unverified", "origin_dehydrated", "compiler_failed", "mini_readme_missing", "ledger_unavailable"]
        missing = [item for item in required if item not in text]
        if missing:
            self.add("failure_modes", "fail", "Failure-mode registry is incomplete.", {"missing": missing})
            return
        self.add("failure_modes", "pass", "Failure-mode registry contains required modes.", {"required": required})

    def gate_forbidden_bypass_markers(self) -> None:
        findings = []
        for scan_root in [self.root / "nexus_gate", self.root / "scripts", self.root / "tests", self.root / "docs"]:
            if not scan_root.exists():
                continue
            for path in scan_root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                    continue
                rel = str(path.relative_to(self.root)).replace("\\", "/")
                if rel in EXCLUDED_SCAN_PATHS:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                for marker in FORBIDDEN_BYPASS_MARKERS:
                    if marker in text:
                        findings.append({"path": rel, "marker": marker})
        if findings:
            self.add("forbidden_bypass_scan", "fail", "Forbidden bypass markers found.", {"findings": findings})
            return
        self.add("forbidden_bypass_scan", "pass", "No forbidden bypass markers found.", {"markers": FORBIDDEN_BYPASS_MARKERS})

    def gate_direct_compiler_calls(self) -> None:
        missing_calls = []
        for rel in MUST_CALL_COMPILER_DIRECTLY:
            path = self.root / rel
            if not path.exists():
                missing_calls.append({"path": rel, "reason": "missing"})
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "nexus_gate.compiler" not in text:
                missing_calls.append({"path": rel, "reason": "does_not_call_gated_compiler_directly"})
        if missing_calls:
            self.add("direct_compiler_calls", "fail", "A required script does not call the gated compiler directly.", {"missing_calls": missing_calls})
            return
        self.add("direct_compiler_calls", "pass", "Compile/once/loop/promote scripts call the gated compiler directly.", {"checked": MUST_CALL_COMPILER_DIRECTLY})

    def gate_python_compile(self) -> None:
        ok = compileall.compile_dir(str(self.root / "nexus_gate"), quiet=1)
        tests_ok = compileall.compile_dir(str(self.root / "tests"), quiet=1)
        if ok and tests_ok:
            self.add("python_compile", "pass", "Python source compiled.", {"paths": ["nexus_gate", "tests"]})
            return
        self.add("python_compile", "fail", "Python compile failed.", {"paths": ["nexus_gate", "tests"]})

    def gate_route_contracts(self) -> None:
        router = NexusRouter()
        cases = {
            "missing_schema": StatePacket("p1", "test", "unit", "", "0.1.3", "read_only_signal", {}),
            "no_authority_tool": StatePacket("p2", "test", "unit", "NEXUS_STATE_PACKET", "0.1.3", "tool_call", {}, authority_scope=[]),
            "read_only": StatePacket("p3", "test", "unit", "NEXUS_STATE_PACKET", "0.1.3", "read_only_signal", {}, authority_scope=[]),
        }
        decisions = {name: router.route(packet).mode for name, packet in cases.items()}
        expected = {"missing_schema": "reject", "no_authority_tool": "shadow", "read_only": "engage"}
        if decisions != expected:
            self.add("route_contracts", "fail", "Core route contracts violated.", {"decisions": decisions, "expected": expected})
            return
        self.add("route_contracts", "pass", "Core route contracts hold.", {"decisions": decisions})

    def gate_unit_tests(self) -> None:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
        try:
            proc = subprocess.run(cmd, cwd=str(self.root), capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired as exc:
            self.add("unit_tests", "fail", "Unit tests timed out.", {"cmd": cmd, "timeout": 60, "error": str(exc)})
            return
        evidence = {"cmd": cmd, "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
        if proc.returncode == 0:
            self.add("unit_tests", "pass", "Unit tests passed.", evidence)
            return
        self.add("unit_tests", "fail", "Unit tests failed.", evidence)

    def gate_ledger_appendable(self) -> None:
        ledger_path = self.root / "ledger" / "nexus_gate_ledger.v0.1.0.jsonl"
        try:
            ledger = JsonlLedger(ledger_path)
            ledger.append({"event": "compiler_ledger_gate_probe", "version": "0.1.3", "status": "probe"})
        except Exception as exc:
            self.add("ledger_appendable", "fail", "Ledger append failed.", {"error": str(exc)})
            return
        self.add("ledger_appendable", "pass", "Ledger is appendable.", {"path": str(ledger_path.relative_to(self.root))})

    def run(self) -> CompileReport:
        start = time.perf_counter()
        self.gate_required_paths()
        self.gate_readme_trisection()
        self.gate_manifest_runtime_laws()
        self.gate_json_files_parse()
        self.gate_mini_readmes()
        self.gate_failure_modes()
        self.gate_forbidden_bypass_markers()
        self.gate_direct_compiler_calls()
        self.gate_python_compile()
        self.gate_route_contracts()
        self.gate_unit_tests()
        self.gate_ledger_appendable()
        failed = [gate for gate in self.gates if gate.failed]
        status = "pass" if not failed else "fail"
        return CompileReport(
            system="NEXUS GATE",
            version="0.1.3-rhp-nexus-ai-compiler",
            root=str(self.root),
            status=status,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            duration_ms=int((time.perf_counter() - start) * 1000),
            gates=[asdict(gate) for gate in self.gates],
        )

    def write_report(self, report: CompileReport) -> Path:
        reports_dir = self.root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = reports_dir / f"nexus_compile_report_{stamp}.json"
        latest = reports_dir / "nexus_compile_report_latest.json"
        encoded = json.dumps(asdict(report), indent=2)
        path.write_text(encoded, encoding="utf-8")
        latest.write_text(encoded, encoding="utf-8")
        JsonlLedger(self.root / "ledger" / "nexus_gate_ledger.v0.1.0.jsonl").append({
            "event": "nexus_compile",
            "version": report.version,
            "status": report.status,
            "report_path": str(path.relative_to(self.root)),
            "duration_ms": report.duration_ms,
            "failed_gates": [gate["gate"] for gate in report.gates if gate["status"] == "fail"],
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
    else:
        print(f"NEXUS GATE compile status: {report.status}")
        print(f"Report: {path}")
    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
