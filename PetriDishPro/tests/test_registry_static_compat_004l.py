import unittest
from pathlib import Path

class RegistryStaticCompat004LTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_all_legacy_and_registry_markers_are_visible(self):
        root = self.root()
        app = (root / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        html = (root / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        overlay = (root / "electron" / "renderer" / "organism_cell_overlay.js").read_text(encoding="utf-8")
        for marker in [
            "PETRI 004L STATIC COMPATIBILITY SEAL",
            "PETRI 004K REAL SCIENCE ORGANISM REGISTRY",
            "PETRI 004H COMPACT LIVE MICROSCOPE DESIGN",
            "visual_contract",
            "schema adapter",
            "requestAnimationFrame(loop);",
            "window.petri.readOrganisms",
            "window.petri.readFieldProfiles",
            "selectedOrganisms",
            "data-org-toggle",
            "behavior driven by registry",
            "function displayNameFor(value)",
            "function normalizeDominantName(run)",
            "function drawCells(ctx,g)",
            "dominant_name",
        ]:
            self.assertIn(marker, app)
        self.assertIn("LIVE SIM", html)
        self.assertIn("Organism Cards", html)
        self.assertIn("drawAmoeba", overlay)
        self.assertIn("discrete morphology overlay", overlay)
        self.assertNotIn("dominant=undefined", app)
        self.assertNotIn("Âµ", app)
        self.assertNotIn("Ã‚", app)

if __name__ == "__main__":
    unittest.main()
