import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronHandoffActionShell(unittest.TestCase):
    def test_main_exposes_hidden_handoff_shell_runner(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("HANDOFF_SCRIPT_MAX_CHARS", main)
        self.assertIn("function runHandoffPowerShell", main)
        self.assertIn('ipcMain.handle("nexus:runHandoffScript"', main)
        self.assertIn("reports\", \"handoff_queue", main)
        self.assertIn("powershell.exe", main)
        self.assertIn("windowsHide: true", main)
        self.assertIn("shell: false", main)
        self.assertIn("NEXUS_HANDOFF_ACTION_SHELL", main)

    def test_preload_exposes_handoff_script_runner(self):
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        self.assertIn("runHandoffScript", preload)
        self.assertIn('ipcRenderer.invoke("nexus:runHandoffScript"', preload)

    def test_renderer_handoff_chat_controls_execution(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("NEX_HANDOFF_ACTION_SHELL_BOUNDARY", renderer)
        self.assertIn("parseHandoffShellAction", renderer)
        self.assertIn('lower.startsWith("/handoff run")', renderer)
        self.assertIn('currentRole() !== "HANDOFF"', renderer)
        self.assertIn("window.nexus.runHandoffScript", renderer)
        self.assertIn("authorized: true", renderer)
        self.assertIn("NEX HANDOFF ACTION REPORT", renderer)

    def test_index_teaches_handoff_run(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("/handoff run", index)
        self.assertIn("hidden backend", index)

    def test_doc_declares_handoff_boundary(self):
        doc = (ROOT / "docs" / "ui" / "NEX_HANDOFF_ACTION_SHELL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.7.4", doc)
        self.assertIn("PowerShell remains the hidden execution substrate", doc)
        self.assertIn("human-initiated `/handoff run`", doc)
        self.assertIn("does not give NEX autonomous shell authority", doc)


if __name__ == "__main__":
    unittest.main()
