import json
import unittest
from pathlib import Path

class NestedPresetSections004YTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_antibiotic_selection_has_nested_metric_cards_section(self):
        root = self.root()
        preset = json.loads((root / 'config' / 'preset_cards.json').read_text(encoding='utf-8'))
        metric = json.loads((root / 'config' / 'metric_cards.json').read_text(encoding='utf-8'))
        self.assertIn('sections', preset['presets']['antibiotic_selection'])
        self.assertIn('metric_cards', preset['presets']['antibiotic_selection']['sections'])
        self.assertIn('kill_curve_proxy', metric['metrics'])

if __name__ == '__main__':
    unittest.main()
