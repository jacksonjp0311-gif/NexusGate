from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_gitnexus_assets_are_linked_from_head(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.3.2.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.3.2.js", html)
        self.assertIn('<script defer src="./nexus_gitnexus_core_hud.v0.3.2.js"', html)

        for version in ("v0.1.0", "v0.1.1", "v0.1.2", "v0.1.3", "v0.2.0", "v0.3.0", "v0.3.1"):
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.css", html)
            self.assertNotIn(f"nexus_gitnexus_core_hud.{version}.js", html)

    def test_gitnexus_does_not_pollute_metrics_body_tail(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<!-- NEXUS_METRICS_HUD_V010_SCRIPT_END -->.*?</body>", html, re.S)
        self.assertIsNotNone(match)
        self.assertNotIn("nexus_gitnexus_core_hud", match.group(0))

    def test_conversation_bridge_active_contract_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_gitnexus_interactive_assets_exist(self):
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.2.css").exists())
        self.assertTrue((ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.2.js").exists())

    def test_mini_dock_is_graphic_plus_button_only(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("gitnexus-mini-canvas", js)
        self.assertIn("Graph Preview", js)
        self.assertIn("Open GitNexus HUD", js)
        self.assertNotIn("data-gitnexus-files", js)
        self.assertNotIn("data-gitnexus-symbols", js)
        self.assertNotIn("data-gitnexus-edges", js)
        self.assertNotIn("data-gitnexus-risk", js)
        self.assertNotIn("gitnexus-core-note", js)
        self.assertNotIn("gitnexus-core-mini", js)

    def test_full_hud_interaction_features_present(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("attachCanvasInteractions", js)
        self.assertIn("onwheel", js)
        self.assertIn("Alt-drag = turn", js)
        self.assertIn("Drag node = move", js)
        self.assertIn("state.transform.rotation", js)
        self.assertIn("data-gn-rotate-left", js)
        self.assertIn("data-gn-rotate-right", js)
        self.assertIn("gitnexusHudWatchdog", js)
        self.assertIn("window.gitnexusHudMount", js)
        self.assertIn("symbol:", js)

    def test_no_iframe_full_hud(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_core_hud.v0.3.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("iframe", js.lower())
        self.assertNotIn("`r`n", js)
        self.assertNotIn("`n", js)


if __name__ == "__main__":
    unittest.main()