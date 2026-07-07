from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.3.0.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.3.0.js", html)
        for version in ("v0.1.0", "v0.1.1", "v0.1.2", "v0.1.3", "v0.2.0"):
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.css", html)
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.js", html)

    def test_gitnexus_interactive_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.0.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.0.js").exists())

    def test_gitnexus_interactive_features_present(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.0.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.0.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("gitnexus-mini-canvas", js)
        self.assertIn("Open Interactive Nexus HUD", js)
        self.assertIn("attachCanvasInteractions", js)
        self.assertIn("onwheel", js)
        self.assertIn("Alt-drag = turn", js)
        self.assertIn("Drag node = move", js)
        self.assertIn("state.transform.rotation", js)
        self.assertIn("symbol:", js)
        self.assertIn("gitnexus-mini-canvas-wrap", css)

    def test_no_iframe_full_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.0.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("iframe", js.lower())


if __name__ == "__main__":
    unittest.main()
