import json
import unittest
from pathlib import Path

class PresetLegacyShape004STests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_legacy_schema_and_nested_shape_markers(self):
        root = self.root()
        preset = json.loads((root / "config" / "preset_cards.json").read_text(encoding="utf-8"))
        metric = json.loads((root / "config" / "metric_cards.json").read_text(encoding="utf-8"))
        self.assertEqual(preset["schema"], "PETRI_PRESET_CARD_REGISTRY.v0.4o")
        self.assertEqual(metric["schema"], "PETRI_METRIC_CARD_REGISTRY.v0.4o")
        self.assertIn("cards", preset)
        self.assertIn("metrics", metric)
        self.assertIn("drug", preset["cards"]["ampicillin_like_proxy"])
        self.assertIn("antibody", preset["cards"]["neutralizing_antibody_proxy"])
        self.assertIn("sparkline", metric["metrics"]["total_cells"])
        self.assertIn("area", metric["metrics"]["shannon_diversity"])
        self.assertIn("bar", metric["metrics"]["dominance_index"])

if __name__ == "__main__":
    unittest.main()
