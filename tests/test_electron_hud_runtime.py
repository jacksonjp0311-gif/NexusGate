import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronHudRuntime(unittest.TestCase):
    def test_package_has_runtime_scripts_and_lockfile(self):
        package = json.loads((ROOT / "electron" / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], "0.3.6")
        self.assertIn("start", package["scripts"])
        self.assertIn("smoke", package["scripts"])
        self.assertTrue((ROOT / "electron" / "package-lock.json").exists())

    def test_visible_titles_are_nexus_gate_only(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        tui = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        self.assertIn("<title>NEXUS GATE</title>", html)
        self.assertIn("<h1>NEXUS GATE</h1>", html)
        self.assertIn("<h1>NEXUS GATE</h1>", tui)
        self.assertNotIn("Hermes-style governed operator surface", html)
        self.assertNotIn("NEXUS GATE <span", tui)

    def test_renderer_contains_photo_aligned_hud_regions(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        for marker in [
            "Process Lanes",
            "Lane Context",
            "NEXUS Console",
            "Feedback Summary",
            "AI Handoff Package",
            "Human Feedback",
            "Data Transfer Protocol",
        ]:
            self.assertIn(marker, html)
        self.assertIn("mini-chart", css)
        self.assertIn("bottom-bus", css)

    def test_main_has_smoke_report_without_expanding_authority(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8")
        self.assertIn("--smoke", main)
        self.assertIn("disableHardwareAcceleration", main)
        self.assertIn("nexus_electron_smoke_report_latest.json", main)
        self.assertIn("shell: false", main)
        self.assertNotIn("exec(", main)
        self.assertNotIn("execFile(", main)

    def test_docs_and_index_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "ELECTRON_HUD_RUNTIME.md").exists())
        index = json.loads(
            (ROOT / "state" / "electron_hud_runtime_index.v0.3.6.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["title"], "NEXUS GATE")
        self.assertIn("bottom_governance_bus", index["hud_regions"])
        self.assertIn("arbitrary_shell_commands", index["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
