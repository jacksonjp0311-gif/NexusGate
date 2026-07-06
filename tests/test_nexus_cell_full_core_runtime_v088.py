import json
import unittest
from pathlib import Path

from nexus_gate.compiler.compiler import NexusCompiler, REQUIRED_PATHS
from nexus_gate.nexus_cell.policy import list_lanes
from nexus_gate.nexus_cell.runner import build_run_packet


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellFullCoreRuntimeV088(unittest.TestCase):
    def test_policy_exposes_controlled_lanes(self):
        lanes = list_lanes()
        for lane in ["status", "compile", "tests", "cell-plan", "cell-context", "cell-bridge"]:
            self.assertIn(lane, lanes)

    def test_run_packet_is_packet_only_without_execute(self):
        packet = build_run_packet(ROOT, lane="cell-bridge", intent="inspect docs only", execute=False, human_authorized=False)
        self.assertEqual(packet["version"], "0.8.8")
        self.assertEqual(packet["mode"], "nexus_cell_full_core_controlled_runner")
        self.assertEqual(packet["authority"]["decision"], "packet_only")
        self.assertFalse(packet["execution"]["executed"])
        self.assertFalse(packet["boundary"]["arbitrary_command_execution"])
        self.assertIn("receipt_id", packet["receipt"])

    def test_execute_request_without_human_authority_is_denied(self):
        packet = build_run_packet(ROOT, lane="compile", intent="compile", execute=True, human_authorized=False)
        self.assertEqual(packet["authority"]["decision"], "packet_only")
        self.assertFalse(packet["execution"]["executed"])
        self.assertIn("execution_requires_human_authorization", packet["authority"]["reasons"])

    def test_manifest_and_command_expose_full_core(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertEqual(manifest["version"], "v0.8.8")
        self.assertEqual(manifest["status"], "full_core_runtime_visible_controlled")
        self.assertTrue(manifest["full_core_runtime"]["enabled"])
        self.assertIn("cell-run", read("scripts/nexus.ps1"))
        self.assertIn("9. Build full core run packet", read("scripts/desktop/open_nexus_gate_console.ps1"))

    def test_compiler_required_paths_and_gate(self):
        for rel in [
            "docs/nexus_cell/NEXUS_CELL_FULL_CORE_RUNTIME.md",
            "nexus_gate/nexus_cell/policy.py",
            "nexus_gate/nexus_cell/authority.py",
            "nexus_gate/nexus_cell/receipt.py",
            "nexus_gate/nexus_cell/runner.py",
            "nexus_gate/nexus_cell/run.py",
        ]:
            self.assertIn(rel, REQUIRED_PATHS)
        compiler = NexusCompiler(ROOT)
        compiler.gate_nexus_cell_full_core_runtime_visibility()
        self.assertEqual(compiler.gates[0].status, "pass")


if __name__ == "__main__":
    unittest.main()
