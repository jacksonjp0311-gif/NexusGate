import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPreflightOptimizerV099(unittest.TestCase):
    def test_preflight_packet_contract(self):
        from nexus_gate.loops.preflight_optimizer import build_preflight_packet
        packet = build_preflight_packet(ROOT, "unit")
        self.assertEqual(packet["schema"], "NEXUS_PREFLIGHT_OPTIMIZER.v0.9.9")
        self.assertEqual(packet["version"], "0.9.9")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertFalse(packet["boundary"]["autonomous_authority"])
        self.assertFalse(packet["boundary"]["git_push_enabled"])
        for gate in ["command_surface_parity", "readme_current_line", "packet_contracts", "bounded_report_shape", "ignored_stage_risk"]:
            self.assertIn(gate, packet["gates"])
        self.assertEqual(packet["gates"]["command_surface_parity"]["status"], "pass")
        self.assertEqual(packet["gates"]["readme_current_line"]["status"], "pass")
        self.assertEqual(packet["gates"]["packet_contracts"]["status"], "pass")

    def test_preflight_docs_and_command_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        doc = (ROOT / "docs" / "runtime" / "NEXUS_PREFLIGHT_OPTIMIZER.md").read_text(encoding="utf-8-sig")
        self.assertIn("v0.9.9 Preflight Optimizer", readme)
        self.assertIn("NEXUS_PREFLIGHT_OPTIMIZER.md", readme)
        self.assertIn("preflight", ps)
        self.assertIn("preflight-json", ps)
        self.assertIn("preflight", sh)
        self.assertIn("preflight-json", sh)
        self.assertIn("stdout = smoke only", doc)
        self.assertLess(len(readme.splitlines()), 220)

    def test_registry_exposes_preflight_optimizer(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(registry["generated_for"], "NEXUS_GATE_v0.9.9")
        self.assertIn("preflight-optimizer", registry["loops"])
        self.assertIn("preflight_optimizer", registry["allowed_commands"])
        self.assertFalse(registry["allowed_commands"]["preflight_optimizer"]["mutates"])
        self.assertFalse(registry["authority_boundary"]["autonomous_authority"])


if __name__ == "__main__":
    unittest.main()
