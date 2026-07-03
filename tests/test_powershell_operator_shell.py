import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPowerShellOperatorShell(unittest.TestCase):
    def test_ui_script_contains_windows_forms_controls(self):
        text = (ROOT / "scripts" / "nexus_ui.ps1").read_text(encoding="utf-8")
        self.assertIn("System.Windows.Forms", text)
        self.assertIn("ComboBox", text)
        self.assertIn("ProgressBar", text)
        self.assertIn("RichTextBox", text)
        self.assertIn("Process Lane", text)
        self.assertIn("Feedback summary", text)
        self.assertIn("Open Feedback Log", text)
        self.assertIn("Open AI Context", text)

    def test_ui_script_contains_required_lanes(self):
        text = (ROOT / "scripts" / "nexus_ui.ps1").read_text(encoding="utf-8")
        for lane in ["evolve", "interface", "feedback", "heal", "status", "compact", "interconnect", "runtime", "pack"]:
            self.assertIn(lane, text)

    def test_command_surface_contains_ui_lane(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"ui"', ps)
        self.assertIn("nexus_ui.ps1", ps)
        self.assertIn("ui)", sh)
        self.assertIn("FAILURE_MODE_CHART", sh)
        self.assertIn("strict", sh)

    def test_ui_docs_and_state_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "NEXUS_PS_SHELL.md").exists())
        state = ROOT / "state" / "nexus_ps_shell_index.v0.2.4.json"
        self.assertTrue(state.exists())
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertIn("process_lane_dropdown", data["ui_features"])
        self.assertIn("progress_buffer_bar", data["ui_features"])
        self.assertIn(".\\scripts\\nexus.ps1 ui", data["commands"])


if __name__ == "__main__":
    unittest.main()
