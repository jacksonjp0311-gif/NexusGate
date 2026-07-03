import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestTuiHudOperatorSurface(unittest.TestCase):
    def test_power_shell_tui_contains_hud_regions(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        for marker in [
            "HUD operator console",
            "PROCESS LANES",
            "NEXUS CONSOLE",
            "FEEDBACK SUMMARY",
            "AI PACKAGE",
            "HUMAN FEEDBACK",
            "SELF-HEALING",
            "INTERCONNECT",
            "GOVERNANCE: strict audit enabled",
        ]:
            self.assertIn(marker, text)

    def test_snapshot_contains_hud_bridge_markup(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        for marker in [
            "class=\"hud\"",
            "AI HANDOFF PACKAGE",
            "DATA TRANSFER PROTOCOL",
            "BOUNDARY: visible and selectable, never self-authorizing",
        ]:
            self.assertIn(marker, text)

    def test_electron_renderer_uses_hud_layout_without_new_authority(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("hud-shell", html)
        self.assertIn("PROCESS LANES", css)
        self.assertIn("AI HANDOFF PACKAGE", html)
        self.assertIn("window.nexus.runLane", js)
        self.assertNotIn("child_process", js)

    def test_hud_docs_and_index_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "TUI_HUD_OPERATOR_SURFACE.md").exists())
        index = json.loads(
            (ROOT / "state" / "tui_hud_operator_surface_index.v0.3.5.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["canonical_command"], ".\\scripts\\nexus.ps1 tui")
        self.assertIn("feedback_summary", index["hud_regions"])
        self.assertIn("run_arbitrary_shell_commands", index["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
