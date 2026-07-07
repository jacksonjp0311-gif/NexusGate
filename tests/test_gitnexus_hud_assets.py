from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"

class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.1.0.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.1.0.js", html)

    def test_gitnexus_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.0.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.1.0.js").exists())
        self.assertTrue((ROOT / "GITNEXUS" / "hud" / "index.html").exists())

if __name__ == "__main__":
    unittest.main()
