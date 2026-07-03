import json
import unittest
from pathlib import Path

from nexus_gate.feedback.interface import compile_ai_feedback_context, write_ai_feedback_interface


ROOT = Path(__file__).resolve().parents[1]


class TestAIFeedbackInterface(unittest.TestCase):
    def test_ai_feedback_context_has_two_way_protocol(self):
        context = compile_ai_feedback_context(ROOT)
        self.assertEqual(context["system"], "NEXUS GATE")
        self.assertIn("two_way_protocol", context)
        self.assertIn("state/ai_feedback_context_latest.json", context["ai_read_surfaces"]["ai_context"])
        self.assertIn("evolve", context["human_commands"])
        self.assertIn("heal", context["human_commands"])
        self.assertIn("interface", context["human_commands"])
        self.assertIn("governed agentic transfer boundary", context["repo_role"])

    def test_interface_writes_ai_context_and_markdown_log(self):
        report = write_ai_feedback_interface(ROOT)
        context_path = ROOT / report.ai_context_path
        log_path = ROOT / report.markdown_log_path
        self.assertTrue(context_path.exists())
        self.assertTrue(log_path.exists())
        context = json.loads(context_path.read_text(encoding="utf-8"))
        self.assertIn("two_way_protocol", context)
        log = log_path.read_text(encoding="utf-8")
        self.assertIn("NEXUS Feedback Interface", log)
        self.assertIn("AI Handoff", log)

    def test_command_surface_contains_interface_lane(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        self.assertIn('"interface"', ps)
        self.assertIn("nexus_gate.feedback.interface_compile", ps)
        self.assertIn("interface)", sh)
        self.assertIn("AI feedback interface", human)
        self.assertIn("Feedback summary", human)

    def test_feedback_docs_exist(self):
        self.assertTrue((ROOT / "docs" / "feedback" / "FEEDBACK_SYSTEM.md").exists())
        self.assertTrue((ROOT / "docs" / "feedback" / "FEEDBACK_LOG.md").exists())
        self.assertTrue((ROOT / "state" / "ai_feedback_interface_index.v0.2.3.json").exists())


if __name__ == "__main__":
    unittest.main()
