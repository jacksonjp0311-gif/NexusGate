import unittest
from pathlib import Path

class LiveMicroscopeDesign004HTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_compact_topbar_and_live_animation_contract(self):
        html = (self.root() / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        js = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        css = (self.root() / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("PETRI 004H COMPACT LIVE MICROSCOPE DESIGN", html)
        self.assertIn("LIVE SIM", html)
        self.assertIn("requestAnimationFrame(loop)", js)
        self.assertIn("Animation rule", js)
        self.assertIn("topbar", css)

    def test_legacy_schema_adapter_contract_still_visible(self):
        js = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function normalizeRun", js)
        self.assertIn("function displayNameFor", js)
        self.assertIn("function normalizeDominantName", js)
        self.assertIn("dominant_name", js)
        self.assertNotIn("dominant=undefined", js)

    def test_morphology_and_overlay_markers_visible(self):
        js = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        overlay = (self.root() / "electron" / "renderer" / "organism_cell_overlay.js").read_text(encoding="utf-8")
        self.assertIn("drawRod", js)
        self.assertIn("drawYeast", js)
        self.assertIn("drawAmoeboid", js)
        self.assertIn("drawAmoeba", overlay)
        self.assertIn("discrete morphology overlay", overlay)

if __name__ == "__main__":
    unittest.main()
