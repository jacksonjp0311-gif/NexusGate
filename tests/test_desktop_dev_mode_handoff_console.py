import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDesktopDevModeHandoffConsole(unittest.TestCase):
    def test_launcher_declares_dev_mode(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Invoke-NexusDevMode", script)
        self.assertIn("NEXUS DEV MODE - Handoff Console", script)
        self.assertIn("Dev Mode / Handoff Console", script)

    def test_launcher_main_menu_routes_dev_mode(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('Write-Host "2. Dev Mode / Handoff Console"', script)
        self.assertIn('elseif ($choice -eq "2")', script)
        self.assertIn("Invoke-NexusDevMode", script)
        self.assertIn('Write-Host "7. Open repo folder"', script)

    def test_dev_mode_has_core_operations(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("Invoke-NexusRuntimeResidueClean", script)
        self.assertIn("Invoke-NexusCompilerSummary", script)
        self.assertIn("Invoke-NexusFullTests", script)
        self.assertIn("Show-LatestHandoffReport", script)
        self.assertIn("git status --short", script)
        self.assertIn("python -m nexus_gate.compiler --root . --json", script)
        self.assertIn("python -m unittest discover -s tests", script)

    def test_dev_mode_doc_exists(self):
        doc = (ROOT / "docs" / "ui" / "NEX_DEV_MODE_HANDOFF_CONSOLE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.7.6", doc)
        self.assertIn("lightweight coding room", doc)
        self.assertIn("The full Electron UI remains the operator dashboard", doc)
        self.assertIn("does not grant model-output authority", doc)


if __name__ == "__main__":
    unittest.main()
