import unittest
from pathlib import Path

class LiveMicroscopeStaticSeal004ITests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_static_compatibility_surface_visible(self):
        app = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("visual_contract", app)
        self.assertIn("window.petri.readConfig", app)
        self.assertIn("function normalizeDominantName", app)
        self.assertIn("function displayNameFor", app)
        self.assertIn("dominant_name", app)
        self.assertIn("drawAmoeba", app)
        self.assertNotIn("dominant=undefined", app)

    def test_live_animation_contract_visible(self):
        app = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        html = (self.root() / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("requestAnimationFrame(loop)", app)
        self.assertIn("Animation rule", app)
        self.assertIn("LIVE SIM", html)

if __name__ == "__main__":
    unittest.main()
