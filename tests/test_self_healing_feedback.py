import unittest
from pathlib import Path

from nexus_gate.self_healing.engine import (
    build_apply_gates,
    build_dry_run_plans,
    compile_self_healing,
    detect_repair_recommendations,
    write_self_healing_report,
)


ROOT = Path(__file__).resolve().parents[1]


class TestSelfHealingFeedback(unittest.TestCase):
    def test_self_healing_report_compiles_without_autonomous_writes(self):
        report = compile_self_healing(ROOT)
        self.assertIn(report.status, {"pass", "warn"})
        self.assertGreaterEqual(len(report.recommendations), 1)
        self.assertGreaterEqual(len(report.dry_run_plans), 1)
        self.assertGreaterEqual(len(report.apply_gates), 1)
        for plan in report.dry_run_plans:
            self.assertEqual(plan["target_writes_performed"], 0)
            self.assertEqual(plan["api_writes_performed"], 0)
            self.assertEqual(plan["git_commits_performed"], 0)
        for gate in report.apply_gates:
            self.assertTrue(gate["human_authorization_required"])
            self.assertEqual(gate["target_writes_performed"], 0)
        path = write_self_healing_report(report, ROOT)
        self.assertTrue(path.exists())

    def test_recommendations_have_cms_required_shape(self):
        recs = detect_repair_recommendations(ROOT)
        for rec in recs:
            self.assertTrue(rec.pressure_source)
            self.assertTrue(rec.repair_class)
            self.assertTrue(rec.allowed_action)
            self.assertEqual(rec.blocked_action, "autonomous_target_write_without_human_authorization")
            self.assertGreaterEqual(len(rec.required_validation), 1)
            self.assertIn("local development evidence", rec.claim_boundary)

    def test_dry_run_and_apply_gate_do_not_write(self):
        recs = detect_repair_recommendations(ROOT)
        plans = build_dry_run_plans(recs)
        gates = build_apply_gates(plans)
        self.assertEqual(len(plans), len(recs))
        self.assertEqual(len(gates), len(plans))
        for plan in plans:
            self.assertEqual(plan.execution_mode, "dry_run_only")
            self.assertIn("no_autonomous_write", plan.blocked_action_preservation)
            self.assertEqual(plan.target_writes_performed, 0)
        for gate in gates:
            self.assertEqual(gate.status, "blocked_until_human_authorized")
            self.assertTrue(gate.human_authorization_required)

    def test_command_surface_contains_heal_lane(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        self.assertIn('"heal"', ps)
        self.assertIn("nexus_gate.self_healing.compile", ps)
        self.assertIn("heal)", sh)
        self.assertIn("FAILURE_MODE_CHART", sh)
        self.assertIn("strict", sh)
        self.assertIn("CRLF will be replaced by LF", human)


if __name__ == "__main__":
    unittest.main()
