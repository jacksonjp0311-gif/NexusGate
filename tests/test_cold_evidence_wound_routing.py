import unittest

from nexus_gate.evidence.cold import ColdEvidenceEngine, ShadowReport


class TestColdEvidenceWoundRouting(unittest.TestCase):
    def test_failed_shadow_report_creates_wound_and_route(self):
        engine = ColdEvidenceEngine()
        report = ShadowReport(
            report_id="shadow-1",
            packet_id="packet-1",
            route_mode="shadow",
            observed_result="mutation_without_authority",
            expected_boundary="must_not_mutate",
            passed=False,
        )
        failure = engine.classify_shadow_report(report)
        self.assertIsNotNone(failure)
        wound = engine.create_wound(failure, affected_surface="runtime")
        route = engine.route_wound(wound)
        self.assertEqual(route.action, "replay")
        self.assertTrue(route.replay_required)
        self.assertFalse(wound.memory_promotion_allowed)

    def test_replay_certificate_controls_memory_promotion(self):
        engine = ColdEvidenceEngine()
        report = ShadowReport(
            report_id="shadow-2",
            packet_id="packet-2",
            route_mode="shadow",
            observed_result="ok_after_fix",
            expected_boundary="must_replay",
            passed=False,
        )
        failure = engine.classify_shadow_report(report)
        wound = engine.create_wound(failure, affected_surface="runtime")
        failed_cert = engine.certify_replay(wound, replay_passed=False, replay_report_path="reports/replay_failed.json")
        passed_cert = engine.certify_replay(wound, replay_passed=True, replay_report_path="reports/replay_passed.json")
        self.assertFalse(failed_cert.memory_promotion_allowed)
        self.assertTrue(passed_cert.memory_promotion_allowed)


if __name__ == "__main__":
    unittest.main()
