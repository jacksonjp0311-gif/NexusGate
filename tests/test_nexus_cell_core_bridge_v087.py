import json
import unittest
from pathlib import Path

from nexus_gate.compiler.compiler import NexusCompiler, REQUIRED_PATHS
from nexus_gate.nexus_cell.bridge import build_cell_bridge_packet
from nexus_gate.nexus_cell.core import build_cell_contract


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellCoreBridgeV087(unittest.TestCase):
    def test_core_contract_is_read_only(self):
        contract = build_cell_contract(ROOT, "inspect docs only", context_limit=6)
        self.assertEqual(contract["version"], "0.8.7")
        self.assertEqual(contract["mode"], "nexus_cell_core_contract_no_execution")
        self.assertFalse(contract["boundary"]["execution_enabled"])
        self.assertIn("cell_contract_id", contract)
        self.assertLessEqual(contract["context_bridge"]["context_ref_count"], 6)

    def test_bridge_packet_requires_human_for_mutation(self):
        packet = build_cell_bridge_packet(ROOT, "git add commit and push a patch", context_limit=8)
        self.assertEqual(packet["mode"], "nexus_cell_core_bridge_no_execution")
        self.assertEqual(packet["cell_contract"]["planner"]["authority_decision"], "shadow")
        self.assertTrue(packet["handoff"]["requires_human_authorization_for_mutation"])
        self.assertIn("git_mutation", packet["handoff"]["blocked_operations"])
        self.assertFalse(packet["boundary"]["execution_enabled"])

    def test_manifest_and_command_expose_core_bridge(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertTrue(str(manifest["version"]).startswith("v0.8."))
        self.assertIn(manifest["status"], {"core_bridge_visible_no_execution", "full_core_runtime_visible_controlled"})
        self.assertTrue(manifest["core_bridge"]["enabled"])
        self.assertIn("cell-bridge", read("scripts/nexus.ps1"))
        self.assertIn("8. Build core bridge packet", read("scripts/desktop/open_nexus_gate_console.ps1"))

    def test_compiler_required_paths_and_gate(self):
        for rel in [
            "docs/nexus_cell/NEXUS_CELL_CORE_BRIDGE.md",
            "nexus_gate/nexus_cell/core.py",
            "nexus_gate/nexus_cell/bridge.py",
        ]:
            self.assertIn(rel, REQUIRED_PATHS)
        compiler = NexusCompiler(ROOT)
        compiler.gate_nexus_cell_core_bridge_visibility()
        self.assertEqual(compiler.gates[0].status, "pass")

    def test_docs_record_core_bridge(self):
        self.assertIn("NexusCell Core Bridge", read("docs/nexus_cell/NEXUS_CELL_CORE_BRIDGE.md"))
        self.assertIn("## v0.8.7 NexusCell Core Bridge Seal", read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md"))


if __name__ == "__main__":
    unittest.main()
