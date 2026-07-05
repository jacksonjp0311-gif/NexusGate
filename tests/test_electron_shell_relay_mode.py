import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronShellRelayMode(unittest.TestCase):
    def test_renderer_declares_shell_relay_boundary(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("NEX_SHELL_RELAY_MODE_BOUNDARY", renderer)
        self.assertIn("parseGovernedChatCommand", renderer)
        self.assertIn('lower.startsWith("/run ")', renderer)
        self.assertIn("formatRelayOutput", renderer)
        self.assertIn("NEX SHELL RELAY REPORT", renderer)

    def test_renderer_routes_run_lane_to_governed_lane(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("await runGovernedLane(command.lane)", renderer)
        self.assertIn("window.nexus.runLane(lane)", renderer)
        self.assertIn("The chat relay only runs allowlisted NEXUS lanes", renderer)
        self.assertIn("arbitrary PowerShell is blocked", renderer)

    def test_selector_is_yellow_black(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS v0.7.3: yellow/black local voice relay selector", css)
        self.assertIn("#role-select option", css)
        self.assertIn("background: #facc15 !important", css)
        self.assertIn("color: #020617 !important", css)

    def test_index_teaches_run_commands(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("Local Voice / Relay", index)
        self.assertIn("/run status", index)
        self.assertIn("/run interconnect", index)

    def test_doc_declares_no_arbitrary_shell(self):
        doc = (ROOT / "docs" / "ui" / "NEX_SHELL_RELAY_MODE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.7.3", doc)
        self.assertIn("PowerShell remains the hidden execution substrate", doc)
        self.assertIn("does not allow arbitrary shell", doc)
        self.assertIn("What ran", doc)


if __name__ == "__main__":
    unittest.main()
