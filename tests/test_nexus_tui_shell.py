import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestNexusTuiShell(unittest.TestCase):
    def test_tui_script_contains_chat_commands_and_lanes(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        for marker in ["NEXUS>", "/run <lane>", "/note <text>", "/packet <summary>", "/debug", "/ai", "/surface", "/graph", "/domains"]:
            self.assertIn(marker, text)
        for lane in ["evolve", "interface", "feedback", "heal", "status", "compact", "interconnect", "runtime", "pack"]:
            self.assertIn(lane, text)

    def test_tui_script_has_buffer_and_colored_output(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        self.assertIn("Render-Bar", text)
        self.assertIn("Write-Progress", text)
        self.assertIn("Color-Line", text)
        self.assertIn("ForegroundColor", text)
        self.assertIn("Show-InterconnectConsole", text)
        self.assertIn("NEXUS INTERCONNECT CONSOLE", text)
        self.assertIn("Show-DomainRoutes", text)

    def test_tui_bounded_repo_changes_are_feedback_only(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        self.assertIn("docs\\feedback\\FEEDBACK_LOG.md", text)
        self.assertIn("docs\\feedback\\operator_packets", text)
        self.assertIn("does not authorize runtime mutation", text)
        self.assertIn("requires_human_authorization", text)

    def test_command_surface_contains_tui_lane(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"tui"', ps)
        self.assertIn("nexus_tui.ps1", ps)
        self.assertIn("tui)", sh)
        self.assertIn("FAILURE_MODE_CHART", sh)
        self.assertIn("strict", sh)

    def test_tui_docs_and_state_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "NEXUS_TUI_SHELL.md").exists())
        state = ROOT / "state" / "nexus_tui_shell_index.v0.2.4b.json"
        self.assertTrue(state.exists())
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertIn("/run <lane>", data["interactive_commands"])
        self.assertIn("append docs/feedback/FEEDBACK_LOG.md", data["bounded_repo_changes"])
        self.assertIn(".\\scripts\\nexus.ps1 tui", data["commands"])


if __name__ == "__main__":
    unittest.main()
