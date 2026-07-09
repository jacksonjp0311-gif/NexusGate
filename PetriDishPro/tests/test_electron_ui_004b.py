import unittest
from pathlib import Path

class ElectronUI004BTests(unittest.TestCase):
    def test_overlay_script_exists(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / 'electron' / 'renderer' / 'organism_cell_overlay.js').read_text(encoding='utf-8')
        self.assertIn('discrete morphology overlay', text)
        self.assertIn('drawRod', text)
        self.assertIn('drawYeast', text)
        self.assertIn('drawAmoeba', text)

    def test_index_loads_overlay(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / 'electron' / 'renderer' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('organism_cell_overlay.js', html)

if __name__ == '__main__':
    unittest.main()
