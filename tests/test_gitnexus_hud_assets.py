from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_upstream_bridge_assets_are_active_once(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_gitnexus_upstream_bridge.v0.5.0.css"), 1)
        self.assertEqual(html.count("nexus_gitnexus_upstream_bridge.v0.5.0.js"), 1)

    def test_old_custom_gitnexus_owners_are_not_active(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        forbidden = [
            "nexus_gitnexus_core_hud",
            "nexus_gitnexus_geometric_mini",
            "nexus_gitnexus_exact_mini_mirror",
            "nexus_gitnexus_scope_hygiene",
            "nexus_gitnexus_scope_switch",
            "nexus_gitnexus_standalone_hud",
        ]
        for token in forbidden:
            self.assertNotIn(token, html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_conversation_output_bridge.v0.2.1f.js"), 1)
        for suffix in ["a", "b", "c", "d", "e"]:
            self.assertNotIn(f"nexus_conversation_output_bridge.v0.2.1{suffix}.js", html)

    def test_upstream_bridge_is_iframe_not_fake_full_graph_engine(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_upstream_bridge.v0.5.0.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "https://gitnexus.vercel.app",
            "http://localhost:4747",
            "gitnexus-upstream-hud",
            "iframe",
            "nexusOpenGitNexus",
        ]:
            self.assertIn(token, js)

    def test_serve_helper_exists(self):
        helper = ROOT / "scripts" / "nexus_gitnexus_upstream.ps1"
        self.assertTrue(helper.exists())
        text = helper.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("gitnexus", text)
        self.assertIn("serve", text)
        self.assertIn("analyze", text)


if __name__ == "__main__":
    unittest.main()