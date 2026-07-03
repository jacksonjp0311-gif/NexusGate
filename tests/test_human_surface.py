import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestHumanSurface(unittest.TestCase):
    def test_human_surface_docs_and_state_exist(self):
        self.assertTrue((ROOT / "docs" / "runtime" / "HUMAN_SURFACE.md").exists())
        self.assertTrue((ROOT / "state" / "human_surface_index.v0.2.1.json").exists())

    def test_human_surface_index_has_law(self):
        data = json.loads((ROOT / "state" / "human_surface_index.v0.2.1.json").read_text(encoding="utf-8"))
        self.assertIn("No operator flood.", data["surface_law"])
        self.assertIn("No CRLF warning noise in normal runs.", data["surface_law"])

    def test_human_script_filters_crlf_warnings(self):
        text = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        self.assertIn("CRLF will be replaced by LF", text)
        self.assertIn("LF will be replaced by CRLF", text)
        self.assertIn("reports\\human_surface", text)

    def test_compact_command_has_human_mode(self):
        text = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        self.assertIn('"human"', text)
        self.assertIn("nexus_human.ps1", text)
        self.assertIn("FAILURE_MODE_CHART", text)
        self.assertIn("UPDATE_CHART", text)


if __name__ == "__main__":
    unittest.main()
