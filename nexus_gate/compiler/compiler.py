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
from nexus_gate.evidence.cold import ColdEvidenceEngine, ShadowReport
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
    "nexus_gate/evidence/cold.py",
    "schemas/state_packet.v0.1.3.schema.json",
    "schemas/failure_mode.v0.1.3.schema.json",
    "schemas/shadow_report.v0.1.5.schema.json",
    "schemas/wound_route.v0.1.5.schema.json",
    "registry/nexus_gate_manifest.v0.1.5.json",
    "state/nexus_gate_state.v0.1.3.json",
    "state/failure_mode_index.v0.1.4.json",
    "state/update_index.v0.1.4.json",
    "state/cold_evidence_index.v0.1.5.json",
    "ledger/nexus_gate_ledger.v0.1.0.jsonl",
    "docs/context/repository_context_index.json",
    "docs/context/rcc_nexus_index.json",
    "docs/context/validation_surface.md",
    "docs/context/REHYDRATION_BOOT.md",
    "docs/context/rehydration_manifest.v0.1.4.json",
    "docs/failure_modes/FAILURE_MODES.md",
    "docs/failure_modes/FAILURE_MODE_CHART.md",
    "docs/failure_modes/WOUND_ROUTING.md",
    "docs/updates/UPDATE_CHART.md",
    "docs/evidence/COLD_EVIDENCE_ENGINE.md",
    "docs/runtime/GATED_RUNTIME_LOOP.md",
    "docs/runtime/RELEASE_GATES.md",
    "docs/runtime/CROSS_PLATFORM_COMMANDS.md",
    "docs/runtime/COMPACT_COMMANDS.md",
    "docs/runtime/STRICT_COMPILER.md",
    "rcc/nexus/README.md",
    "rcc/nexus/route_map.json",
    "rcc/nexus/task_routing_matrix.md",
    "rcc/nexus/echo_location_template.md",
    "rcc/nexus/agent_handoff_contract.md",
    "scripts/nexus.ps1",
    "scripts/nexus.sh",
    "scripts/nexus_compile.ps1",
    "scripts/nexus_once.ps1",
    "scripts/nexus_dev_loop.ps1",
    "scripts/nexus_promote.ps1",
    "scripts/nexus_compile.sh",
    "scripts/nexus_once.sh",
    "scripts/nexus_dev_loop.sh",
    "scripts/nexus_promote.sh",
    "scripts/nexus_strict_compile.ps1",
    "scripts/nexus_strict_compile.sh",
    "nexus_gate/nexus_cell/plan.py",
    "docs/nexus_cell/NEXUS_CELL_CONTEXT_BRIDGE.md",
    "nexus_gate/nexus_cell/context_bridge.py",
    "nexus_gate/nexus_cell/bridge.py",
    "nexus_gate/nexus_cell/run.py",
    "nexus_gate/nexus_cell/runner.py",
    "nexus_gate/nexus_cell/receipt.py",
    "nexus_gate/nexus_cell/authority.py",
    "nexus_gate/nexus_cell/policy.py",
    "docs/nexus_cell/NEXUS_CELL_FULL_CORE_RUNTIME.md",
    "nexus_gate/nexus_cell/core.py",
    "docs/nexus_cell/NEXUS_CELL_CORE_BRIDGE.md",
    "nexus_gate/nexus_shell/shell.py",
    "nexus_gate/nexus_shell/__main__.py",
    "nexus_gate/nexus_shell/__init__.py",
    "state/nexus_shell/shell_manifest.v0.8.6.json",
    "docs/nexus_shell/NEXUS_SHELL_OPERATOR.md",
    "NexusShell/README.md",
    "nexus_gate/nexus_cell/__init__.py",
    "state/nexus_cell/cell_manifest.v0.8.4.json",
    "docs/nexus_cell/NEXUS_CELL_PLANNER.md",
    "docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md",
    "NexusCell/README.md",
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
    "Every new runtime loop must exist in both PowerShell and Bash.",
    "No rehydration without failure chart visibility.",
]

REQUIRED_RUNTIME_LAWS = [
    "No adapter, no bridge.",
    "No schema, no route.",
    "No authority verification, no mutation.",
    "No replay certificate, no memory promotion.",
    "No wound route, no retrust.",
    "No ledger stub, no compounding.",
    "No shadow failure without wound route.",
]

MUST_CALL_COMPILER_DIRECTLY = [
    "scripts/nexus.ps1",
    "scripts/nexus_compile.ps1",
    "scripts/nexus_once.ps1",
    "scripts/nexus_dev_loop.ps1",
    "scripts/nexus_promote.ps1",
    "scripts/nexus_strict_compile.ps1",
    "scripts/nexus.sh",
    "scripts/nexus_compile.sh",
    "scripts/nexus_once.sh",
    "scripts/nexus_dev_loop.sh",
    "scripts/nexus_promote.sh",
    "scripts/nexus_strict_compile.sh",
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
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        missing = [m for m in REQUIRED_README_MARKERS if m not in text]
        if missing:
            self.add("readme_trisection", "fail", "README missing required markers.", {"missing": missing})
            return
        self.add("readme_trisection", "pass", "README contains Human/RHP Nexus/AI and rehydration markers.", {"markers": REQUIRED_README_MARKERS})

    def gate_manifest_runtime_laws(self) -> None:
        manifest_path = self.root / "registry" / "nexus_gate_manifest.v0.1.5.json"
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
        roots = ["schemas", "registry", "state", "docs/context", "rcc/nexus"]
        json_files: list[Path] = []
        for rel in roots:
            root = self.root / rel
            if root.exists():
                json_files.extend(root.glob("*.json"))
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
        path = self.root / "docs/failure_modes/FAILURE_MODE_CHART.md"
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        required = [
            "schema_missing",
            "authority_unverified",
            "origin_dehydrated",
            "compiler_failed",
            "mini_readme_missing",
            "ledger_unavailable",
            "shadow_failure_unrouted",
            "replay_missing",
            "bash_env_unavailable",
        ]
        missing = [item for item in required if item not in text]
        if missing:
            self.add("failure_modes", "fail", "Failure-mode chart is incomplete.", {"missing": missing})
            return
        self.add("failure_modes", "pass", "Failure-mode chart contains required modes.", {"required": required})

    def gate_rehydration_visibility(self) -> None:
        manifest_path = self.root / "docs/context/rehydration_manifest.v0.1.4.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("rehydration_visibility", "fail", "Rehydration manifest failed to parse.", {"error": str(exc)})
            return
        required = [
            "docs/failure_modes/FAILURE_MODE_CHART.md",
            "docs/updates/UPDATE_CHART.md",
            "reports/nexus_compile_report_latest.json",
        ]
        declared = manifest.get("agent_must_read_before_patch", [])
        missing = [item for item in required if item not in declared]
        if missing:
            self.add("rehydration_visibility", "fail", "Rehydration manifest missing visibility surfaces.", {"missing": missing})
            return
        self.add("rehydration_visibility", "pass", "Rehydration requires failure/update/report visibility.", {"required": required})

    def gate_update_chart_current(self) -> None:
        path = self.root / "docs/updates/UPDATE_CHART.md"
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        required = ["v0.1.5", "Strict compiler", "Cold Evidence", "No version step without update chart entry"]
        missing = [item for item in required if item not in text]
        if missing:
            self.add("update_chart_current", "fail", "Update chart missing current v0.1.5 state.", {"missing": missing})
            return
        self.add("update_chart_current", "pass", "Update chart includes current v0.1.5 state.", {"required": required})

    def gate_cold_evidence_contracts(self) -> None:
        doc = self.root / "docs/evidence/COLD_EVIDENCE_ENGINE.md"
        wound = self.root / "docs/failure_modes/WOUND_ROUTING.md"
        index = self.root / "state/cold_evidence_index.v0.1.5.json"
        for path in [doc, wound, index]:
            if not path.exists():
                self.add("cold_evidence_contracts", "fail", "Cold evidence surface missing.", {"missing": str(path.relative_to(self.root))})
                return
        text = doc.read_text(encoding="utf-8", errors="ignore") + "\n" + wound.read_text(encoding="utf-8", errors="ignore")
        required = ["ShadowReport", "ShadowFailure", "ShadowWound", "WoundRoute", "ReplayCertificate", "DemotionDecision"]
        missing = [item for item in required if item not in text]
        if missing:
            self.add("cold_evidence_contracts", "fail", "Cold evidence docs missing required contracts.", {"missing": missing})
            return

        try:
            data = json.loads(index.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("cold_evidence_contracts", "fail", "Cold evidence index failed to parse.", {"error": str(exc)})
            return

        if not data.get("rehydration_required", False):
            self.add("cold_evidence_contracts", "fail", "Cold evidence index must be visible on rehydration.", {})
            return

        self.add("cold_evidence_contracts", "pass", "Cold evidence and wound route contracts are visible.", {"contracts": required})

    def gate_cold_evidence_engine(self) -> None:
        engine = ColdEvidenceEngine()
        report = ShadowReport(
            report_id="compiler-shadow-report",
            packet_id="compiler-packet",
            route_mode="shadow",
            observed_result="tool_call_without_authority",
            expected_boundary="must_not_engage",
            passed=False,
        )
        failure = engine.classify_shadow_report(report)
        if failure is None:
            self.add("cold_evidence_engine", "fail", "Failed shadow report did not classify.", {})
            return
        wound = engine.create_wound(failure, affected_surface="compiler")
        route = engine.route_wound(wound)
        cert = engine.certify_replay(wound, replay_passed=True, replay_report_path="reports/compiler_replay.json")
        if route.replay_required and cert.memory_promotion_allowed:
            self.add("cold_evidence_engine", "pass", "Cold evidence engine classifies failure, wounds, routes, and certifies replay.", {
                "failure": failure.failure_mode,
                "wound_status": wound.status,
                "route_action": route.action,
                "replay_passed": cert.replay_passed,
            })
            return
        self.add("cold_evidence_engine", "fail", "Cold evidence engine contract failed.", {})

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
        self.add("direct_compiler_calls", "pass", "Compile/loop/promote/strict scripts call the gated compiler directly.", {"checked": MUST_CALL_COMPILER_DIRECTLY})

    def gate_compact_commands(self) -> None:
        required = ["scripts/nexus.ps1", "scripts/nexus.sh", "docs/runtime/COMPACT_COMMANDS.md"]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("compact_commands", "fail", "Compact command surface missing.", {"missing": missing})
            return
        text = (self.root / "docs/runtime/COMPACT_COMMANDS.md").read_text(encoding="utf-8", errors="ignore")
        if "One command surface." not in text or "Less syntax." not in text:
            self.add("compact_commands", "fail", "Compact command docs missing command law.", {})
            return
        self.add("compact_commands", "pass", "Compact command surface is present.", {"required": required})


    def gate_nexus_cell_planner_visibility(self) -> None:
        required = [
            "NexusCell/README.md",
            "docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md",
            "docs/nexus_cell/NEXUS_CELL_PLANNER.md",
            "state/nexus_cell/cell_manifest.v0.8.4.json",
            "nexus_gate/nexus_cell/__init__.py",
            "nexus_gate/nexus_cell/plan.py",
            "scripts/nexus.ps1",
            "scripts/desktop/open_nexus_gate_console.ps1",
        ]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell planner surface missing.", {"missing": missing})
            return

        try:
            manifest = json.loads((self.root / "state/nexus_cell/cell_manifest.v0.8.4.json").read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell manifest failed to parse.", {"error": str(exc)})
            return

        forbidden = set(manifest.get("desktop_portal", {}).get("forbidden_surfaces", []))
        required_forbidden = {"execute code", "enable backend", "claim rollback"}
        missing_forbidden = sorted(required_forbidden - forbidden)
        if missing_forbidden:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell forbidden boundary is incomplete.", {"missing": missing_forbidden})
            return

        if manifest.get("status") not in {"compiler_visible_planner_no_execution", "context_bridge_visible_no_execution", "operator_shell_visible_no_execution", "core_bridge_visible_no_execution", "full_core_runtime_visible_controlled"}:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell planner status is not an accepted read-only compiler-visible status.", {"status": manifest.get("status")})
            return

        try:
            from nexus_gate.nexus_cell.plan import build_plan
            plan = build_plan(self.root, "inspect docs only")
        except Exception as exc:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell planner could not build a read-only plan.", {"error": str(exc)})
            return

        boundary = plan.get("boundary", {}) if isinstance(plan, dict) else {}
        if boundary.get("execution_enabled") is not False:
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell planner boundary allowed execution.", {"boundary": boundary})
            return
        if plan.get("mode") != "read_only_planner_no_execution":
            self.add("nexus_cell_planner_visibility", "fail", "NexusCell planner mode drifted.", {"mode": plan.get("mode")})
            return

        latest_report = self.root / "reports" / "nexus_cell_plan_latest.json"
        latest_state = self.root / "state" / "nexus_cell" / "planner_state_latest.json"
        visible_outputs = {
            "latest_report_exists": latest_report.exists(),
            "latest_state_exists": latest_state.exists(),
        }

        self.add("nexus_cell_planner_visibility", "pass", "NexusCell planner is compiler-visible and read-only bounded.", {
            "version": manifest.get("version"),
            "status": manifest.get("status"),
            "planner_mode": plan.get("mode"),
            "authority_decision": plan.get("authority_decision"),
            "risk_score": plan.get("risk_score"),
            "visible_outputs": visible_outputs,
            "claim_boundary": plan.get("claim_boundary"),
        })

    def gate_nexus_cell_context_bridge_visibility(self) -> None:
        required = [
            "docs/nexus_cell/NEXUS_CELL_CONTEXT_BRIDGE.md",
            "nexus_gate/nexus_cell/context_bridge.py",
            "state/nexus_cell/cell_manifest.v0.8.4.json",
        ]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("nexus_cell_context_bridge_visibility", "fail", "NexusCell context bridge surface missing.", {"missing": missing})
            return
        try:
            manifest = json.loads((self.root / "state/nexus_cell/cell_manifest.v0.8.4.json").read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("nexus_cell_context_bridge_visibility", "fail", "NexusCell manifest failed to parse.", {"error": str(exc)})
            return
        if manifest.get("status") not in {"context_bridge_visible_no_execution", "operator_shell_visible_no_execution", "core_bridge_visible_no_execution", "full_core_runtime_visible_controlled"}:
            self.add("nexus_cell_context_bridge_visibility", "fail", "NexusCell context bridge status is not an accepted active status.", {"status": manifest.get("status")})
            return
        try:
            from nexus_gate.nexus_cell.context_bridge import build_context_bridge
            packet = build_context_bridge(self.root, "inspect docs only", limit=8)
        except Exception as exc:
            self.add("nexus_cell_context_bridge_visibility", "fail", "Context bridge failed to build packet.", {"error": str(exc)})
            return
        boundary = packet.get("boundary", {})
        if boundary.get("execution_enabled") is not False or boundary.get("file_contents_embedded") is not False:
            self.add("nexus_cell_context_bridge_visibility", "fail", "Context bridge boundary drifted.", {"boundary": boundary})
            return
        self.add("nexus_cell_context_bridge_visibility", "pass", "NexusCell context bridge is compiler-visible and read-only bounded.", {
            "version": manifest.get("version"),
            "status": manifest.get("status"),
            "mode": packet.get("mode"),
            "context_ref_count": packet.get("context_ref_count"),
            "claim_boundary": packet.get("claim_boundary"),
        })


    def gate_nexus_shell_operator_visibility(self) -> None:
        required = [
            "NexusShell/README.md",
            "docs/nexus_shell/NEXUS_SHELL_OPERATOR.md",
            "state/nexus_shell/shell_manifest.v0.8.6.json",
            "nexus_gate/nexus_shell/shell.py",
            "scripts/nexus.ps1",
            "scripts/desktop/open_nexus_gate_console.ps1",
        ]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("nexus_shell_operator_visibility", "fail", "NexusShell operator surface missing.", {"missing": missing})
            return
        try:
            manifest = json.loads((self.root / "state/nexus_shell/shell_manifest.v0.8.6.json").read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("nexus_shell_operator_visibility", "fail", "NexusShell manifest failed to parse.", {"error": str(exc)})
            return
        if manifest.get("status") != "operator_shell_visible_no_execution":
            self.add("nexus_shell_operator_visibility", "fail", "NexusShell status drifted.", {"status": manifest.get("status")})
            return
        try:
            from nexus_gate.nexus_shell.shell import build_shell_packet
            packet = build_shell_packet(self.root, "inspect docs only", command="status", context_limit=6)
        except Exception as exc:
            self.add("nexus_shell_operator_visibility", "fail", "NexusShell failed to build packet.", {"error": str(exc)})
            return
        boundary = packet.get("boundary", {})
        if boundary.get("execution_enabled") is not False or boundary.get("shell_mutation_enabled") is not False:
            self.add("nexus_shell_operator_visibility", "fail", "NexusShell boundary drifted.", {"boundary": boundary})
            return
        self.add("nexus_shell_operator_visibility", "pass", "NexusShell operator is compiler-visible and no-execution bounded.", {
            "version": manifest.get("version"),
            "status": manifest.get("status"),
            "mode": packet.get("mode"),
            "available_commands": packet.get("available_commands"),
            "claim_boundary": packet.get("claim_boundary"),
        })


    def gate_nexus_cell_core_bridge_visibility(self) -> None:
        required = [
            "docs/nexus_cell/NEXUS_CELL_CORE_BRIDGE.md",
            "nexus_gate/nexus_cell/core.py",
            "nexus_gate/nexus_cell/bridge.py",
            "state/nexus_cell/cell_manifest.v0.8.4.json",
            "scripts/nexus.ps1",
            "scripts/desktop/open_nexus_gate_console.ps1",
        ]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("nexus_cell_core_bridge_visibility", "fail", "NexusCell core bridge surface missing.", {"missing": missing})
            return
        try:
            manifest = json.loads((self.root / "state/nexus_cell/cell_manifest.v0.8.4.json").read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("nexus_cell_core_bridge_visibility", "fail", "NexusCell manifest failed to parse.", {"error": str(exc)})
            return
        if manifest.get("status") not in {"core_bridge_visible_no_execution", "full_core_runtime_visible_controlled"}:
            self.add("nexus_cell_core_bridge_visibility", "fail", "NexusCell core bridge status is not accepted.", {"status": manifest.get("status")})
            return
        try:
            from nexus_gate.nexus_cell.bridge import build_cell_bridge_packet
            packet = build_cell_bridge_packet(self.root, "inspect docs only", context_limit=6)
        except Exception as exc:
            self.add("nexus_cell_core_bridge_visibility", "fail", "NexusCell core bridge failed to build packet.", {"error": str(exc)})
            return
        boundary = packet.get("boundary", {})
        if boundary.get("execution_enabled") is not False or boundary.get("process_spawn_enabled") is not False:
            self.add("nexus_cell_core_bridge_visibility", "fail", "NexusCell bridge boundary drifted.", {"boundary": boundary})
            return
        self.add("nexus_cell_core_bridge_visibility", "pass", "NexusCell core bridge is compiler-visible and no-execution bounded.", {
            "version": manifest.get("version"),
            "status": manifest.get("status"),
            "mode": packet.get("mode"),
            "cell_phase": packet.get("cell_contract", {}).get("cell_phase"),
            "claim_boundary": packet.get("claim_boundary"),
        })


    def gate_nexus_cell_full_core_runtime_visibility(self) -> None:
        required = [
            "docs/nexus_cell/NEXUS_CELL_FULL_CORE_RUNTIME.md",
            "nexus_gate/nexus_cell/policy.py",
            "nexus_gate/nexus_cell/authority.py",
            "nexus_gate/nexus_cell/receipt.py",
            "nexus_gate/nexus_cell/runner.py",
            "nexus_gate/nexus_cell/run.py",
            "state/nexus_cell/cell_manifest.v0.8.4.json",
            "scripts/nexus.ps1",
            "scripts/desktop/open_nexus_gate_console.ps1",
        ]
        missing = [rel for rel in required if not (self.root / rel).exists()]
        if missing:
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell full core runtime surface missing.", {"missing": missing})
            return
        try:
            manifest = json.loads((self.root / "state/nexus_cell/cell_manifest.v0.8.4.json").read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell manifest failed to parse.", {"error": str(exc)})
            return
        if manifest.get("status") != "full_core_runtime_visible_controlled":
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell full core runtime status is not active.", {"status": manifest.get("status")})
            return
        try:
            from nexus_gate.nexus_cell.runner import build_run_packet
            packet = build_run_packet(self.root, lane="cell-bridge", intent="inspect docs only", execute=False, human_authorized=False)
        except Exception as exc:
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell full core failed to build packet.", {"error": str(exc)})
            return
        boundary = packet.get("boundary", {})
        if boundary.get("arbitrary_command_execution") is not False:
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell full core exposed arbitrary execution.", {"boundary": boundary})
            return
        if packet.get("execution", {}).get("executed") is not False:
            self.add("nexus_cell_full_core_runtime_visibility", "fail", "NexusCell full core executed during visibility gate.", {"execution": packet.get("execution")})
            return
        self.add("nexus_cell_full_core_runtime_visibility", "pass", "NexusCell full core runtime is compiler-visible and controlled.", {
            "version": manifest.get("version"),
            "status": manifest.get("status"),
            "mode": packet.get("mode"),
            "lane": packet.get("lane"),
            "authority": packet.get("authority"),
            "receipt_id": packet.get("receipt", {}).get("receipt_id"),
            "claim_boundary": packet.get("claim_boundary"),
        })

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
            "missing_schema": StatePacket("p1", "test", "unit", "", "0.1.5", "read_only_signal", {}),
            "no_authority_tool": StatePacket("p2", "test", "unit", "NEXUS_STATE_PACKET", "0.1.5", "tool_call", {}, authority_scope=[]),
            "read_only": StatePacket("p3", "test", "unit", "NEXUS_STATE_PACKET", "0.1.5", "read_only_signal", {}, authority_scope=[]),
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
            ledger.append({"event": "compiler_ledger_gate_probe", "version": "0.1.5", "status": "probe"})
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
        self.gate_rehydration_visibility()
        self.gate_update_chart_current()
        self.gate_cold_evidence_contracts()
        self.gate_cold_evidence_engine()
        self.gate_forbidden_bypass_markers()
        self.gate_direct_compiler_calls()
        self.gate_compact_commands()
        self.gate_nexus_cell_planner_visibility()
        self.gate_nexus_cell_context_bridge_visibility()
        self.gate_nexus_cell_core_bridge_visibility()
        self.gate_nexus_cell_full_core_runtime_visibility()
        self.gate_nexus_shell_operator_visibility()
        self.gate_python_compile()
        self.gate_route_contracts()
        self.gate_unit_tests()
        self.gate_ledger_appendable()
        failed = [gate for gate in self.gates if gate.failed]
        status = "pass" if not failed else "fail"
        return CompileReport(
            system="NEXUS GATE",
            version="0.1.5-strict-cold-evidence-compiler",
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
