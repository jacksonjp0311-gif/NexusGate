import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDesktopDevModeCleanSafety(unittest.TestCase):
    def test_dev_clean_uses_git_untracked_discovery(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Invoke-NexusRuntimeResidueClean", script)
        self.assertIn("git ls-files --others --exclude-standard -- reports", script)
        self.assertIn("removing untracked timestamped report JSON files only", script)
        self.assertIn("second safety restore", script)

    def test_dev_clean_does_not_broad_delete_root_reports(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertNotIn("Get-ChildItem -Path $reportRoot -File", script)
        self.assertNotIn("Where-Object { $_.Name -match '^nexus_.*_report_20", script)

    def test_dev_clean_doc_records_safety_rule(self):
        doc = (ROOT / "docs" / "ui" / "NEX_DEV_MODE_HANDOFF_CONSOLE.md").read_text(encoding="utf-8-sig")
        self.assertIn("v0.7.6.1 Dev Clean Safety", doc)
        self.assertIn("must never delete tracked historical report files", doc)
        self.assertIn("cleanup must classify tracked versus untracked before deletion", doc)


if __name__ == "__main__":
    unittest.main()
