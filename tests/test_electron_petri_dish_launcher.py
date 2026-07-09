from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ElectronPetriDishLauncherTests(unittest.TestCase):
    def test_petri_launcher_surface_exists(self) -> None:
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn('id="petri-open"', html)
        self.assertIn('id="petri-mini-body"', html)
        self.assertIn("PetriDishPro mini launcher", html)
        self.assertNotIn('class="metric-row metric-next"', html)

    def test_metrics_are_compressed_to_open_petri_space(self) -> None:
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("grid-template-columns: 314px 260px minmax(0, 1fr)", html)
        self.assertIn(".petri-dish-mini", html)
        self.assertIn("grid-column: 3 / 4", html)

    def test_petri_bridge_is_fixed_not_lane_authority(self) -> None:
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("openPetriDishProWindow", main)
        self.assertIn("PetriDishPro", main)
        self.assertIn("petri:run", main)
        self.assertIn("openPetriDishPro", preload)
        self.assertIn("openPetriDishPro", renderer)
        allowlist_block = main.split("const ALLOWLISTED_COMMANDS", 1)[1].split("]);", 1)[0]
        self.assertNotIn("petri", allowlist_block.lower())


if __name__ == "__main__":
    unittest.main()
