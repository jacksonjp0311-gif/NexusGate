import json
import unittest
from pathlib import Path

from nexus_gate.reflection.reflective_loop import compile_reflective_loop, write_reflective_loop_report


ROOT = Path(__file__).resolve().parents[1]


class TestReflectiveIntelligenceLoop(unittest.TestCase):
    def test_reflective_doctrine_exists(self):
        text = (ROOT / "docs" / "intelligence" / "REFLECTIVE_INTELLIGENCE_LOOP.md").read_text(encoding="utf-8")
        self.assertIn("Reflective intelligence is permitted.", text)
        self.assertIn("Autonomous authority is not.", text)
        self.assertIn("The loop may adapt, improvise, and overcome.", text)
        self.assertIn("Passing gates is evidence", text)

    def test_reflective_compiler_report_can_be_generated(self):
        report = compile_reflective_loop(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertIn("chatgpt_handoff", report.allowed_interfaces)
        self.assertIn("codex_handoff", report.allowed_interfaces)
        self.assertIn("self_authorize", report.blocked_actions)
        path = write_reflective_loop_report(report, ROOT)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertIn("reports/tui/nexus_tui_ai_handoff_latest.txt", data["read_surfaces"])
        self.assertIn("autonomous authority", data["claim_boundary"])

    def test_scripts_expose_reflect_lane(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"reflect"', ps)
        self.assertIn("nexus_gate.reflection.compile", human)
        self.assertIn("reflect)", sh)
        self.assertIn("nexus_gate.reflection.compile", sh)


if __name__ == "__main__":
    unittest.main()
