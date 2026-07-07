from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.1.2.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.1.2.js", html)
        self.assertNotIn("nexus_gitnexus_core_hud.v0.1.0.css", html)
        self.assertNotIn("nexus_gitnexus_core_hud.v0.1.0.js", html)
        self.assertNotIn("nexus_gitnexus_core_hud.v0.1.1.css", html)
        self.assertNotIn("nexus_gitnexus_core_hud.v0.1.1.js", html)

    def test_gitnexus_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.2.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.2.js").exists())
        self.assertTrue((ROOT / "GITNEXUS" / "hud" / "index.html").exists())

    def test_gitnexus_mount_targets_left_neural_activity_slot(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn(".left-stack", js)
        self.assertIn("NEURAL ACTIVITY", js)
        self.assertIn("left-rail-after-neural-activity", js)
        self.assertIn("insertAdjacentElement", js)
        self.assertIn("gitnexus-core-program", js)

    def test_no_iframe_full_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("iframe", js.lower())


if __name__ == "__main__":
    unittest.main()
