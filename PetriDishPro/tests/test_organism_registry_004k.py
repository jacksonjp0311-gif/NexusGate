import json
import unittest
from pathlib import Path
class OrganismRegistry004KTests(unittest.TestCase):
    def root(self): return Path(__file__).resolve().parents[1]
    def test_registry_has_science_grounded_defaults(self):
        cfg=json.loads((self.root()/"config"/"organisms.json").read_text(encoding="utf-8")); ids={o["id"] for o in cfg["organisms"]}
        self.assertIn("ecoli_k12_proxy",ids); self.assertIn("bacillus_subtilis_proxy",ids); self.assertIn("saccharomyces_cerevisiae_proxy",ids); self.assertIn("acanthamoeba_castellanii_proxy",ids)
        morphs={o["morphology"]["render_type"] for o in cfg["organisms"]}; self.assertIn("rod",morphs); self.assertIn("rod_spore",morphs); self.assertIn("budding_yeast",morphs); self.assertIn("amoeboid",morphs)
    def test_renderer_selection_binding_contract(self):
        app=(self.root()/"electron"/"renderer"/"app.js").read_text(encoding="utf-8")
        self.assertIn("selectedOrganisms",app); self.assertIn("data-org-toggle",app); self.assertIn("readOrganisms",app); self.assertIn("behavior driven by registry",app)
        self.assertIn("function normalizeDominantName",app); self.assertIn("dominant_name",app); self.assertIn("requestAnimationFrame(loop)",app)
        self.assertNotIn("dominant=undefined",app); self.assertNotIn("Ã‚",app); self.assertNotIn("Âµ",app)
    def test_electron_bridge_reads_registry(self):
        main=(self.root()/"electron"/"main.js").read_text(encoding="utf-8"); preload=(self.root()/"electron"/"preload.js").read_text(encoding="utf-8")
        self.assertIn("petri:readOrganisms",main); self.assertIn("config/organisms.json",main); self.assertIn("readOrganisms",preload)
if __name__ == "__main__": unittest.main()
