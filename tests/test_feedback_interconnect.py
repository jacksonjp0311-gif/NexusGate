import json
import unittest
from pathlib import Path

from nexus_gate.evidence.compact import compile_evidence_compaction, write_compaction_report
from nexus_gate.feedback.engine import compile_feedback, write_feedback_report
from nexus_gate.interconnect.graph import build_interconnect, write_interconnect_report


ROOT = Path(__file__).resolve().parents[1]


class TestFeedbackInterconnect(unittest.TestCase):
    def test_evidence_compaction_compiles(self):
        report = compile_evidence_compaction(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertGreaterEqual(report.file_count, 1)
        path = write_compaction_report(report, ROOT)
        self.assertTrue(path.exists())

    def test_interconnect_graph_compiles(self):
        report = build_interconnect(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertGreaterEqual(len(report.nodes), 5)
        self.assertGreaterEqual(len(report.edges), 5)
        self.assertTrue(report.graph_hash)
        paths = write_interconnect_report(report, ROOT)
        self.assertTrue(Path(paths["latest"]).exists())
        self.assertTrue(Path(paths["graph"]).exists())

    def test_feedback_report_compiles(self):
        compaction = compile_evidence_compaction(ROOT)
        write_compaction_report(compaction, ROOT)
        interconnect = build_interconnect(ROOT)
        write_interconnect_report(interconnect, ROOT)
        report = compile_feedback(ROOT)
        self.assertIn(report.status, {"pass", "warn"})
        self.assertGreater(report.health_score, 0)
        path = write_feedback_report(report, ROOT)
        self.assertTrue(path.exists())

    def test_command_surface_contains_evolve_lanes(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        self.assertIn('"feedback"', ps)
        self.assertIn('"interconnect"', ps)
        self.assertIn('"compact"', ps)
        self.assertIn('"evolve"', ps)
        self.assertIn("nexus_gate.feedback.compile", ps)
        self.assertIn("nexus_gate.interconnect.compile", ps)
        self.assertIn("nexus_gate.evidence.compact", ps)
        self.assertIn("nexus_gate.adapters.compile", ps)


if __name__ == "__main__":
    unittest.main()
