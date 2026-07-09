import json
import unittest
from pathlib import Path

class ScienceMicroscope004CTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_science_config_has_real_morphology_contract(self):
        cfg = json.loads((self.root() / "config" / "petri_science_config.v0.4c.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["schema"], "PETRI_SCIENCE_VISUAL_CONFIG.v0.4c")
        morph = {v["morphology"] for v in cfg["organisms"].values()}
        self.assertIn("rod", morph)
        self.assertIn("budding_yeast", morph)
        self.assertIn("amoeboid", morph)
        self.assertEqual(cfg["dish"]["shape"], "circle")

    def test_renderer_uses_config_and_avoids_square_field_wound(self):
        app = (self.root() / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("drawCells", app)
        self.assertIn("drawField", app)
        self.assertIn("ctx.arc(cx, cy, r", app)
        self.assertIn("visual_contract", app)
        self.assertIn("window.petri.readConfig", app)

    def test_electron_ipc_contract_visible(self):
        main = (self.root() / "electron" / "main.js").read_text(encoding="utf-8")
        preload = (self.root() / "electron" / "preload.js").read_text(encoding="utf-8")
        self.assertIn("petri:run", main)
        self.assertIn("petri:readConfig", main)
        self.assertIn("readConfig", preload)

if __name__ == "__main__":
    unittest.main()
