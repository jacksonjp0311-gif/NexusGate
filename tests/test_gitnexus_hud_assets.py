from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.1.3.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.1.3.js", html)
        for version in ("v0.1.0", "v0.1.1", "v0.1.2"):
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.css", html)
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.js", html)

    def test_gitnexus_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.3.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.3.js").exists())

    def test_gitnexus_uses_floating_left_dock(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.3.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.3.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("gitnexus-core-left-dock", js)
        self.assertIn("floating-left-empty-slot", js)
        self.assertIn("findNeuralActivityRect", js)
        self.assertIn("position: fixed", css)
        self.assertIn("gitnexus-core-program", js)

    def test_no_iframe_full_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.3.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("iframe", js.lower())


if __name__ == "__main__":
    unittest.main()
