from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


EXPECTED_GITNEXUS_ASSETS = [
    "nexus_gitnexus_standalone_hud.v0.4.1.css",
    "nexus_gitnexus_standalone_hud.v0.4.1.js",
]

FORBIDDEN_GITNEXUS_TOKENS = [
    "nexus_gitnexus_core_hud",
    "nexus_gitnexus_geometric_mini",
    "nexus_gitnexus_exact_mini_mirror",
    "nexus_gitnexus_scope_hygiene",
    "nexus_gitnexus_scope_switch",
    "nexus_gitnexus_standalone_hud.v0.4.0",
]

ACTIVE_BRIDGE = "nexus_conversation_output_bridge.v0.2.1f.js"
INACTIVE_BRIDGES = [
    "nexus_conversation_output_bridge.v0.2.1a.js",
    "nexus_conversation_output_bridge.v0.2.1b.js",
    "nexus_conversation_output_bridge.v0.2.1c.js",
    "nexus_conversation_output_bridge.v0.2.1d.js",
    "nexus_conversation_output_bridge.v0.2.1e.js",
]


class TestGitNexusHudAssets(unittest.TestCase):
    def test_expected_runtime_safe_standalone_assets_are_present_once(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        for asset in EXPECTED_GITNEXUS_ASSETS:
            self.assertEqual(html.count(asset), 1, asset)

    def test_old_gitnexus_owner_assets_are_not_active(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN_GITNEXUS_TOKENS:
            self.assertNotIn(token, html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count(ACTIVE_BRIDGE), 1)
        for bridge in INACTIVE_BRIDGES:
            self.assertNotIn(bridge, html)

    def test_runtime_safe_behavior_exists(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_standalone_hud.v0.4.1.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "gitnexus-core-left-dock",
            "gitnexus-standalone-hud",
            "gnx-mini-canvas-v041",
            "gnx-full-canvas-v041",
            "state.fullVisible",
            "cancelAnimationFrame(state.fullRaf)",
            "bindRuntimeSafeHotkeys",
            "if (!open) return;",
            "gitnexusOpenHud",
        ]:
            self.assertIn(token, js)

    def test_runtime_safe_css_exists(self):
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_standalone_hud.v0.4.1.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "gnx-mini-dock",
            "gnx-mini-v041",
            "gnx-hud-v041",
            "gnx-full-canvas-v041",
        ]:
            self.assertIn(token, css)


if __name__ == "__main__":
    unittest.main()