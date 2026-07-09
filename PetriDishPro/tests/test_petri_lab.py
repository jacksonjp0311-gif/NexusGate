import tempfile, unittest
from pathlib import Path
from petri_lab.presets import list_presets
from petri_lab.simulation import run_experiment
class PetriLabTests(unittest.TestCase):
    def test_presets_exist(self):
        p=list_presets(); self.assertIn("microbial_competition",p); self.assertIn("antibiotic_selection",p); self.assertIn("cellular_tissue",p); self.assertIn("biofilm_dormancy",p)
    def test_run_emits_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); r=run_experiment(root,"microbial_competition",steps=6,grid_size=16,seed=7)
            self.assertEqual(r["validation"]["status"],"pass"); self.assertTrue((root/"reports"/"bio"/"petri_run_latest.json").exists()); self.assertGreater(r["metrics"]["total_population"],0)
    def test_claim_boundary_locked(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=run_experiment(Path(tmp),"antibiotic_selection",steps=5,grid_size=14,seed=11)
            self.assertEqual(r["claim_level"],"educational_research_simulation_only"); self.assertIn("not clinical", r["claim_boundary"].lower())
if __name__ == "__main__": unittest.main()
