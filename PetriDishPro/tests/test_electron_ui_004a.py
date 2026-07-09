from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ElectronUi004ATests(unittest.TestCase):
    def test_renderer_has_schema_adapter(self):
        app = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function normalizeRun", app)
        self.assertIn("function displayNameFor", app)
        self.assertIn("dominant_name", app)
        self.assertNotIn("dominant=undefined", app)

    def test_electron_has_artifact_archive_bridge(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8")
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8")
        self.assertIn("petri:listRuns", main)
        self.assertIn("petri:openArtifacts", main)
        self.assertIn("listRuns", preload)
        self.assertIn("openArtifacts", preload)

    def test_index_has_refined_workbench_surfaces(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Electron Microscope Workbench", html)
        self.assertIn("metrics", html)
        self.assertIn("Run Archive", html)
        self.assertIn("gridOverlay", html)

if __name__ == "__main__":
    unittest.main()
