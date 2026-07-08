from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_geometric_mini_overlay_is_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.5.css", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.5.js", html)
        self.assertNotIn("nexus_gitnexus_exact_mini_mirror.v0.3.4", html)

    def test_conversation_bridge_active_contract_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_geometric_mini_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.5.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.5.js").exists())

    def test_geometric_mini_is_simple_canvas_not_dashboard_clone(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.5.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("gitnexus-geometric-mini-canvas", js)
        self.assertIn("CODEGRAPH GEOMETRY", js)
        self.assertIn("LIVE CODEGRAPH", js)
        self.assertIn("CLICK TO OPEN HUD", js)
        self.assertNotIn("gitnexus-exact-mini", js)
        self.assertNotIn("gitnexus-mini-mirror-shell", js)

    def test_popup_sanitizer_and_open_bridge_exist(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.5.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("sanitizeToolbarLabels", js)
        self.assertIn("openBigHud", js)
        self.assertIn("TURN", js)
        self.assertIn("EDGES", js)
        self.assertIn("LABELS", js)


if __name__ == "__main__":
    unittest.main()