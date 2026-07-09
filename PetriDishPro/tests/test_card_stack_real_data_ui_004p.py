import json
import unittest
from pathlib import Path

class CardStackRealDataUI004PTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_expanded_organism_registry_and_source_gate(self):
        cfg = json.loads((self.root() / "config" / "organisms.json").read_text(encoding="utf-8"))
        ids = {o["id"] for o in cfg["organisms"]}
        for expected in ["pseudomonas_aeruginosa_proxy", "staphylococcus_aureus_proxy", "salmonella_enterica_proxy", "vibrio_cholerae_proxy", "lactobacillus_proxy"]:
            self.assertIn(expected, ids)
        self.assertIn("ChEMBL", cfg["sources"])
        self.assertIn("EUCAST", cfg["sources"])

    def test_preset_and_metric_cards_exist(self):
        root = self.root()
        presets = json.loads((root / "config" / "preset_cards.json").read_text(encoding="utf-8"))
        metrics = json.loads((root / "config" / "metric_cards.json").read_text(encoding="utf-8"))
        self.assertIn("drug_response_screen", presets["presets"])
        self.assertIn("antibody_binding_screen", presets["presets"])
        ids = {m["id"] for m in metrics["cards"]}
        self.assertIn("kill_curve_proxy", ids)
        self.assertIn("antibody_occupancy_proxy", ids)

    def test_renderer_card_stack_contract(self):
        root = self.root()
        app = (root / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        css = (root / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("PETRI 004P CARD STACK REAL DATA UI", app)
        self.assertIn("renderEmergentConditions", app)
        self.assertIn("human_readable_particle_state_receipt", app)
        self.assertIn("metrics_stack_bottom_left", app)
        self.assertIn(".metric-stack", css)
        self.assertIn(".emergent-panel", css)

    def test_entry_card_mirror_visible(self):
        text = (self.root() / "ORGANISM_GATE.ps1").read_text(encoding="utf-8")
        self.assertIn("PETRI 004P ENTRY CARD MIRROR", text)
        self.assertIn("Data Gates", text)

if __name__ == "__main__":
    unittest.main()
