import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestCompactRuntimeSurface(unittest.TestCase):
    def test_compact_scripts_exist(self):
        self.assertTrue((ROOT / "scripts" / "nexus.ps1").exists())
        self.assertTrue((ROOT / "scripts" / "nexus.sh").exists())

    def test_compact_scripts_preserve_gates(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        for text in [ps, sh]:
            self.assertIn("nexus_gate.compiler", text)
            self.assertIn("FAILURE_MODE_CHART", text)
            self.assertIn("UPDATE_CHART", text)

    def test_compact_docs_exist(self):
        text = (ROOT / "docs" / "runtime" / "COMPACT_COMMANDS.md").read_text(encoding="utf-8")
        self.assertIn("One command surface.", text)
        self.assertIn("Less syntax.", text)
        self.assertIn("No compile pass, no promotion.", text)


if __name__ == "__main__":
    unittest.main()
