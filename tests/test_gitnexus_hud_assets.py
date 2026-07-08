from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_single_owner_gitnexus_v037_assets_are_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.js", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.js", html)

        forbidden = re.findall(
            r"nexus_gitnexus_(?:core_hud|geometric_mini|exact_mini_mirror)\.v(?!0\.3\.7)\d+\.\d+\.\d+\.(?:css|js)",
            html,
        )
        self.assertEqual(sorted(set(forbidden)), [])

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_core_no_longer_owns_mini_dock(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.7.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.7.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("core HUD no longer owns", css)
        self.assertIn("function ensureDock()", js)
        self.assertIn("createBigHud();", js)
        self.assertNotIn("setInterval(renderMiniMirror", js)

    def test_mini_singleton_owner_exists(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_geometric_mini.v0.3.7.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("removeDuplicateDocks", js)
        self.assertIn("STATE_KEY", js)
        self.assertIn("if (state.raf) return;", js)
        self.assertIn("gitnexus-geometric-mini-canvas", js)
        self.assertIn("CLICK TO OPEN HUD", js)
        self.assertNotIn("gitnexus-exact-mini", js)
        self.assertNotIn("gitnexus-mini-mirror-shell", js)

    def test_no_gitnexus_in_metrics_body_tail(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<!-- NEXUS_METRICS_HUD_V010_SCRIPT_END -->.*?</body>", html, re.S)
        if match:
            self.assertNotIn("nexus_gitnexus_core_hud", match.group(0))
            self.assertNotIn("nexus_gitnexus_geometric_mini", match.group(0))


if __name__ == "__main__":
    unittest.main()