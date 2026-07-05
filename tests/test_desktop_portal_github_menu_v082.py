import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDesktopPortalGithubMenuV082(unittest.TestCase):
    def test_launcher_has_github_docs_submenu(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("https://github.com/jacksonjp0311-gif/NexusGate", script)
        self.assertIn("function Invoke-NexusResourceMenu", script)
        self.assertIn("GitHub / README / Docs", script)
        self.assertIn("[9] GitHub / README / Docs", script)
        self.assertIn("Open GitHub repository", script)
        self.assertIn("Open GitHub README", script)
        self.assertIn("docs/ENTRYPOINTS.md", script)
        self.assertIn("NEXUS_CHANGELOG.md", script)

    def test_main_readme_mentions_submenu(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("GitHub / README / Docs", readme)
        self.assertIn("observable, diagnosable, bounded", readme)
        self.assertIn("Failure Modes / Doctor Gateway", readme)

    def test_entrypoints_mentions_submenu_and_repo(self):
        entrypoints = (ROOT / "docs" / "ENTRYPOINTS.md").read_text(encoding="utf-8")
        self.assertIn("GitHub / README / Docs Submenu", entrypoints)
        self.assertIn("Open GitHub repository", entrypoints)
        self.assertIn("https://github.com/jacksonjp0311-gif/NexusGate", entrypoints)


if __name__ == "__main__":
    unittest.main()
