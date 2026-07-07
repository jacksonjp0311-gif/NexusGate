from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.2.0.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.2.0.js", html)
        for version in ("v0.1.0", "v0.1.1", "v0.1.2", "v0.1.3"):
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.css", html)
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.js", html)

    def test_gitnexus_big_nexus_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.2.0.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.2.0.js").exists())

    def test_gitnexus_uses_canvas_big_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.2.0.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.2.0.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("gitnexus-big-canvas", js)
        self.assertIn("Open Big Nexus HUD", js)
        self.assertIn("buildModel", js)
        self.assertIn("relax(model)", js)
        self.assertIn("gitnexus-big", css)
        self.assertIn("grid-template-columns: 260px minmax(0, 1fr) 310px", css)

    def test_no_iframe_full_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.2.0.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("iframe", js.lower())


if __name__ == "__main__":
    unittest.main()
