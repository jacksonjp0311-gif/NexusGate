import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestReadmeRehydrationV082(unittest.TestCase):
    def test_root_readme_is_compact_but_preserves_required_markers(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertLess(len(text.splitlines()), 220)
        for marker in [
            "Reflective Intelligence Layer for AI Systems",
            "local-first reflective intelligence layer for AI systems",
            "The portal is only the doorway",
            "observable, diagnosable, bounded",
            "## NEXUS Connective Point",
            "Human Director Box",
            "PART I - Human README",
            "PART II - RHP Nexus README",
            "PART III - AI Agent README",
            "RHP Origin Alignment",
            "AI Operating Contract",
            "Failure Modes",
            "v0.8.1 UI cleanup line",
            "GitHub / README / Docs",
            "No RHP alignment, no durable mutation.",
            "No mini README, no blind patching.",
            "Every new runtime loop must exist in both PowerShell and Bash.",
            "No rehydration without failure chart visibility.",
        ]:
            self.assertIn(marker, text)

    def test_bulk_readme_history_moved_to_docs(self):
        self.assertTrue((ROOT / "docs" / "readme" / "NEXUS_README_EXTENDED_REFERENCE.md").exists())
        self.assertTrue((ROOT / "docs" / "versioning" / "NEXUS_CHANGELOG.md").exists())
        changelog = (ROOT / "docs" / "versioning" / "NEXUS_CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("README = orientation and entrypoint", changelog)
        self.assertIn("v0.2.4b - PowerShell HUD TUI", changelog)
        self.assertIn("v0.8.2D README/doc rehydration", changelog)

    def test_entrypoints_and_algorithm_docs_exist(self):
        entrypoints = (ROOT / "docs" / "ENTRYPOINTS.md").read_text(encoding="utf-8")
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8")
        self.assertIn("Desktop Entry Portal", entrypoints)
        self.assertIn("GitHub / README / Docs Submenu", entrypoints)
        self.assertIn("PowerShell", entrypoints)
        self.assertIn("Bash", entrypoints)
        self.assertIn("Rehydration Algorithm", algorithms)
        self.assertIn("Failure Doctor Algorithm", algorithms)
        self.assertIn("Compiler Gate Algorithm", algorithms)

    def test_mini_readmes_have_echo_location(self):
        for rel in [
            "docs/README.md",
            "scripts/README.md",
            "docs/readme/README.md",
            "docs/algorithms/README.md",
            "electron/README.md",
        ]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("RCC Nexus Echo Location", text)


if __name__ == "__main__":
    unittest.main()
