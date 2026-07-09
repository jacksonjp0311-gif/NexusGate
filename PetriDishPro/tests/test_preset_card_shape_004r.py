import json
import unittest
from pathlib import Path

class PresetCardShape004RTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_004o_schema_and_004p_content_version_coexist(self):
        root = self.root()
        preset = json.loads((root / "config" / "preset_cards.json").read_text(encoding="utf-8"))
        metric = json.loads((root / "config" / "metric_cards.json").read_text(encoding="utf-8"))
        self.assertEqual(preset["schema"], "PETRI_PRESET_CARD_REGISTRY.v0.4o")
        self.assertEqual(metric["schema"], "PETRI_METRIC_CARD_REGISTRY.v0.4o")
        self.assertEqual(preset["content_version"], "004P")
        self.assertEqual(metric["content_version"], "004P")

    def test_top_level_legacy_shapes_exist(self):
        root = self.root()
        preset = json.loads((root / "config" / "preset_cards.json").read_text(encoding="utf-8"))
        metric = json.loads((root / "config" / "metric_cards.json").read_text(encoding="utf-8"))
        self.assertIn("cards", preset)
        self.assertIn("metrics", metric)
        self.assertIn("ampicillin_like_proxy", preset["cards"])
        self.assertIn("neutralizing_antibody_proxy", preset["cards"])
        self.assertIn("total_cells", metric["metrics"])
        self.assertIn("shannon_diversity", metric["metrics"])
        self.assertIn("dominance_index", metric["metrics"])

if __name__ == "__main__":
    unittest.main()
