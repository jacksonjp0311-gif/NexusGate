import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from nexus_gate.build.packer import CRITICAL_GOAL_LANES, build_bundle, run_command


ROOT = Path(__file__).resolve().parents[1]


class TestPackagingGoalLock(unittest.TestCase):
    def test_goal_lock_exists_and_has_lanes(self):
        path = ROOT / "state" / "goal_lock.v0.1.6.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("governed transfer boundary", data["goal"])
        for lane in ["adapter", "authority", "hot_route", "cold_evidence", "wound_route", "compiler"]:
            self.assertIn(lane, data["lanes"])

    def test_packer_collects_manifest_without_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = build_bundle(ROOT, Path(tmp), run_checks=False)
            self.assertEqual(report.status, "pass")
            self.assertGreater(report.file_count, 10)
            self.assertGreater(report.total_bytes, 1000)
            self.assertIn("compiler", report.goal_lanes)

    def test_compact_command_has_pack_mode(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn("pack", ps)
        self.assertIn("pack", sh)
        self.assertIn("nexus_gate.build.packer", ps + sh)

    def test_packer_timeout_is_structured(self):
        old_timeout = os.environ.get("NEXUS_PACK_CHECK_TIMEOUT_SECONDS")
        os.environ["NEXUS_PACK_CHECK_TIMEOUT_SECONDS"] = "1"
        try:
            result = run_command(ROOT, [sys.executable, "-c", "import time; time.sleep(3)"])
        finally:
            if old_timeout is None:
                os.environ.pop("NEXUS_PACK_CHECK_TIMEOUT_SECONDS", None)
            else:
                os.environ["NEXUS_PACK_CHECK_TIMEOUT_SECONDS"] = old_timeout
        self.assertEqual(result["returncode"], 124)
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["timeout_seconds"], 1)
        self.assertIn("timed out", result["stderr_tail"])


if __name__ == "__main__":
    unittest.main()
