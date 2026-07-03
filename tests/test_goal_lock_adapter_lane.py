import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestGoalLockAdapterLane(unittest.TestCase):
    def test_goal_lock_allows_adapter_lane(self):
        data = json.loads((ROOT / "state" / "goal_lock.v0.1.6.json").read_text(encoding="utf-8"))
        self.assertIn("adapter", data["lanes"])

    def test_adapter_docs_exist(self):
        self.assertTrue((ROOT / "docs" / "adapters" / "ADAPTER_REGISTRY.md").exists())
        self.assertTrue((ROOT / "docs" / "adapters" / "LOCAL_DEMO_ADAPTER.md").exists())

    def test_compact_command_has_adapters_mode(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        self.assertIn("adapters", ps)
        self.assertIn("nexus_gate.adapters.compile", ps)


if __name__ == "__main__":
    unittest.main()
