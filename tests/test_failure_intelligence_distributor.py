import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.failure_intelligence.distributor import build_packet, compile_from_log


class TestFailureIntelligenceDistributor(unittest.TestCase):
    def test_compile_missing_marker_from_unittest_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "full-tests.log"
            log.write_text(
                "FAIL: test_marker (tests.test_x.TestX.test_marker)\n"
                "Traceback (most recent call last):\n"
                "  File \"tests/test_x.py\", line 1, in test_marker\n"
                "AssertionError: 'human-readable, AI-parsable, and troubleshootable' not found in 'README'\n"
                "FAILED (failures=1)\n",
                encoding="utf-8",
            )
            packet = compile_from_log(log)
            self.assertEqual(packet["failed_count"], 1)
            self.assertIn("HUMAN_READABLE_AI_PARSABLE_AND_TROUBLESHOOTABLE", packet["wound_id"])
            self.assertEqual(packet["failures"][0]["missing_marker"], "human-readable, AI-parsable, and troubleshootable")

    def test_build_packet_uses_existing_report_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "nexus_compiled_failure_latest.json").write_text(json.dumps({
                "wound_id": "TEST_WOUND",
                "stage": "full-tests",
                "failed_count": 1,
                "failures": [{"suggested_fix": "patch target"}],
                "stability_lock": "BLOCKED",
            }), encoding="utf-8")
            packet = build_packet(root)
            self.assertEqual(packet["wound_id"], "TEST_WOUND")
            self.assertEqual(packet["next_close_target"], "patch target")


if __name__ == "__main__":
    unittest.main()
