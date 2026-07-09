import json
import unittest
from pathlib import Path

class PresetCards004OTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_preset_card_registry_has_drug_and_antibody_presets(self):
        cfg = json.loads((self.root() / 'config' / 'preset_cards.json').read_text(encoding='utf-8'))
        self.assertEqual(cfg['schema'], 'PETRI_PRESET_CARD_REGISTRY.v0.4o')
        self.assertIn('drug_response_screen', cfg['presets'])
        self.assertIn('antibody_binding_screen', cfg['presets'])
        self.assertIn('ampicillin_like_proxy', cfg['cards'])
        self.assertIn('igg_opsonization_proxy', cfg['cards'])
        self.assertIn('metric_cards', cfg['presets']['antibiotic_selection']['sections'])

    def test_metric_registry_has_chart_contract(self):
        cfg = json.loads((self.root() / 'config' / 'metric_cards.json').read_text(encoding='utf-8'))
        self.assertEqual(cfg['schema'], 'PETRI_METRIC_CARD_REGISTRY.v0.4o')
        for key in ['total_cells', 'kill_curve_proxy', 'binding_occupancy', 'shannon_diversity']:
            self.assertIn(key, cfg['metrics'])
            self.assertIn('chart', cfg['metrics'][key])

    def test_electron_dashboard_and_entry_mirror_visible(self):
        root = self.root()
        main = (root / 'electron' / 'main.js').read_text(encoding='utf-8')
        preload = (root / 'electron' / 'preload.js').read_text(encoding='utf-8')
        html = (root / 'electron' / 'renderer' / 'index.html').read_text(encoding='utf-8')
        dash = (root / 'electron' / 'renderer' / 'dashboardCards.js').read_text(encoding='utf-8')
        gate = (root / 'ORGANISM_GATE.ps1').read_text(encoding='utf-8')
        self.assertIn('petri:readPresetCards', main)
        self.assertIn('readMetricCards', preload)
        self.assertIn('dashboardCards.js', html)
        self.assertIn('Preset Cards', dash)
        self.assertIn('drawMiniChart', dash)
        self.assertIn('PETRI 004O ENTRY CARD MIRROR WRAPPER', gate)

if __name__ == '__main__':
    unittest.main()
