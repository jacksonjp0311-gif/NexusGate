import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestTuiElectronBridge(unittest.TestCase):
    def test_tui_bridge_commands_exist(self):
        text = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8")
        for marker in [
            "/copy",
            "/snapshot",
            "/electron",
            "/graph",
            "/domains",
            "nexus_tui_ai_handoff_latest.txt",
            "nexus_tui_snapshot_latest.html",
            "Interconnect Checks",
            "Placeholder Evidence",
            "mutate graph state",
            "Set-Clipboard",
            "Allowed commands: evolve, interface, feedback, heal, status, compact, interconnect, runtime, pack",
        ]:
            self.assertIn(marker, text)

    def test_ui_alias_routes_to_terminal_tui(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        ui = (ROOT / "scripts" / "nexus_ui.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"ui"', ps)
        self.assertIn('"ui" { powershell -ExecutionPolicy Bypass -File .\\scripts\\nexus_ui.ps1 }', ps)
        self.assertIn("nexus_tui.ps1", ui)
        self.assertIn("System.Windows.Forms", ui)
        self.assertIn("ui)", sh)
        self.assertIn("tui)", sh)

    def test_bridge_docs_and_state_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "TUI_TO_ELECTRON_PORT_PLAN.md").exists())
        state = ROOT / "state" / "tui_to_electron_bridge_index.v0.2.5.json"
        self.assertTrue(state.exists())
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertIn("/copy", data["interactive_commands"])
        self.assertIn("evolve", data["electron_allowlist"])
        self.assertIn("reports/tui/nexus_tui_snapshot_latest.html", data["electron_read_surfaces"])
        self.assertIn("arbitrary_shell_commands", data["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
