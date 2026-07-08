from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_geometric_mini_v036_is_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.6.css", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.6.js", html)
        self.assertNotIn("nexus_gitnexus_geometric_mini.v0.3.5.css", html)
        self.assertNotIn("nexus_gitnexus_geometric_mini.v0.3.5.js", html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_v036_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.6.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.6.js").exists())

    def test_singleton_mount_logic_exists(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.6.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("removeDuplicateDocks", js)
        self.assertIn("MutationObserver", js)
        self.assertIn("state.raf", js)
        self.assertIn("if (state.raf) return;", js)
        self.assertIn("scheduleLayout", js)
        self.assertNotIn("setInterval(boot", js)

    def test_simple_geometric_ui_still_present(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.6.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("GITNEXUS", js)
        self.assertIn("CODEGRAPH GEOMETRY", js)
        self.assertIn("LIVE CODEGRAPH", js)
        self.assertIn("CLICK TO OPEN HUD", js)


if __name__ == "__main__":
    unittest.main()