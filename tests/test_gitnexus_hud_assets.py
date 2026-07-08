from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_local_hud_v052_assets_are_active_once(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_gitnexus_local_hud.v0.5.2.css"), 1)
        self.assertEqual(html.count("nexus_gitnexus_local_hud.v0.5.2.js"), 1)

    def test_remote_or_old_gitnexus_owners_are_not_active(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        forbidden = [
            "nexus_gitnexus_upstream_bridge",
            "gitnexus.vercel.app",
            "localhost:4747",
            "nexus_gitnexus_core_hud",
            "nexus_gitnexus_geometric_mini",
            "nexus_gitnexus_exact_mini_mirror",
            "nexus_gitnexus_scope_hygiene",
            "nexus_gitnexus_scope_switch",
            "nexus_gitnexus_standalone_hud",
            "nexus_gitnexus_local_hud.v0.5.1",
        ]
        for token in forbidden:
            self.assertNotIn(token, html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_conversation_output_bridge.v0.2.1f.js"), 1)
        for suffix in ["a", "b", "c", "d", "e"]:
            self.assertNotIn(f"nexus_conversation_output_bridge.v0.2.1{suffix}.js", html)

    def test_local_hud_is_dynamic_and_not_remote(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.2.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("gitnexus.vercel.app", js)
        self.assertNotIn("localhost:4747", js)
        self.assertNotIn("<iframe", js)
        for token in [
            "gitnexus-local-hud",
            "gnx-local-mini-canvas",
            "gnx-local-full-canvas",
            "tickPhysics",
            "updateCamera",
            "focusNode",
            "FORCE",
            "ORBIT",
            "CIRCLE",
            "ALT-DRAG / SHIFT-WHEEL = ROTATE",
            "nexusOpenGitNexus",
            "nexusGitNexusRefresh",
        ]:
            self.assertIn(token, js)

    def test_local_hud_css_exists(self):
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.2.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "gnx-local-mini-dock",
            "gnx-local-hud",
            "gnx-local-canvas-shell",
            "gnx-local-top-files",
        ]:
            self.assertIn(token, css)


if __name__ == "__main__":
    unittest.main()