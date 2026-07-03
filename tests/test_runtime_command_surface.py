import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestRuntimeCommandSurface(unittest.TestCase):
    def test_runtime_docs_and_scripts_exist(self):
        self.assertTrue((ROOT / "docs" / "bridge" / "BOUNDED_BRIDGE_RUNTIME.md").exists())
        self.assertTrue((ROOT / "scripts" / "nexus_runtime.ps1").exists())
        self.assertTrue((ROOT / "scripts" / "nexus_runtime.sh").exists())

    def test_compact_command_has_runtime_mode(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn("runtime", ps)
        self.assertIn("runtime", sh)
        self.assertIn("nexus_gate.bridge.runtime_compiler", ps + sh)
        self.assertIn("FAILURE_MODE_CHART", ps)
        self.assertIn("UPDATE_CHART", ps)


if __name__ == "__main__":
    unittest.main()
