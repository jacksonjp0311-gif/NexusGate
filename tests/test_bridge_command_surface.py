import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestBridgeCommandSurface(unittest.TestCase):
    def test_bridge_docs_and_scripts_exist(self):
        self.assertTrue((ROOT / "docs" / "bridge" / "BRIDGE_SESSION_RUNNER.md").exists())
        self.assertTrue((ROOT / "scripts" / "nexus_bridge_demo.ps1").exists())
        self.assertTrue((ROOT / "scripts" / "nexus_bridge_demo.sh").exists())

    def test_compact_command_has_bridge_mode(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn("bridge", ps)
        self.assertIn("bridge", sh)
        self.assertIn("nexus_gate.bridge.compile", ps + sh)


if __name__ == "__main__":
    unittest.main()
