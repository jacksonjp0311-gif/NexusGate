from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_local_hud_v053_assets_are_active_once(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_gitnexus_local_hud.v0.5.3.css"), 1)
        self.assertEqual(html.count("nexus_gitnexus_local_hud.v0.5.3.js"), 1)

    def test_old_or_remote_gitnexus_owners_are_not_active(self):
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
            "nexus_gitnexus_local_hud.v0.5.2",
        ]
        for token in forbidden:
            self.assertNotIn(token, html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(html.count("nexus_conversation_output_bridge.v0.2.1f.js"), 1)
        for suffix in ["a", "b", "c", "d", "e"]:
            self.assertNotIn(f"nexus_conversation_output_bridge.v0.2.1{suffix}.js", html)

    def test_geometry_analyzer_and_modes_exist(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.3.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertNotIn("gitnexus.vercel.app", js)
        self.assertNotIn("localhost:4747", js)
        self.assertNotIn("<iframe", js)
        for token in [
            "GEOMETRY ANALYZER",
            "analyzeGeometry",
            "bridgePressure",
            "anisotropy",
            "category entropy",
            "SPEED_PROFILES",
            "FAST",
            "SLOW",
            "FILTER_LABELS",
            "MODE HOT",
            "MODE CHANGED",
            "MODE CORE",
            "labelAllowed",
            "selected-node focus path",
            "buildDiagnostics",
            "Centrality",
            "Blast Radius",
            "Dead Islands",
            "Bridge Risk",
            "Change Priority",
            "countVisibleForMode",
            "activeCategories",
            "data-category",
            "data-category-files",
        ]:
            self.assertIn(token, js)

    def test_mode_all_and_category_filters_are_bounded(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.3.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn('setFilterMode("all"', js)
        self.assertIn("if (!nodes.length)", js)
        self.assertIn("state.search = \"\"", js)
        self.assertIn("state.activeCategories[category]", js)
        self.assertIn("visibleFileNodes", js)

    def test_gitnexus_layout_compacts_search_and_right_top_files(self):
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.3.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "grid-template-columns: 270px minmax(320px, 0.72fr) minmax(520px, 1fr)",
            ".gnx-local-controls",
            ".gnx-category-filter",
            ".gnx-category-files",
            ".gnx-geometry-summary",
            ".gnx-diagnostics",
            "[data-top-files-right]",
            "max-height: 150px",
        ]:
            self.assertIn(token, css)

    def test_geometry_css_exists(self):
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.3.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in ["gnx-local-mini-dock", "gnx-local-hud", "gnx-geometry-panel", "is-changed"]:
            self.assertIn(token, css)


if __name__ == "__main__":
    unittest.main()
