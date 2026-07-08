from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_only_runtime_safe_standalone_asset_is_active(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_standalone_hud.v0.4.1.css", html)
        self.assertIn("nexus_gitnexus_standalone_hud.v0.4.1.js", html)

        # Correct form: \s is whitespace. Do not write \\s here, because that
        # excludes the literal letter "s" inside the character class.
        active = sorted(set(re.findall(r'nexus_gitnexus_[^"\s<>]+\.(?:css|js)', html)))
        self.assertEqual(active, [
            "nexus_gitnexus_standalone_hud.v0.4.1.css",
            "nexus_gitnexus_standalone_hud.v0.4.1.js",
        ])

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

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

    def test_no_old_owner_tokens_in_index(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        for token in [
            "nexus_gitnexus_core_hud",
            "nexus_gitnexus_geometric_mini",
            "nexus_gitnexus_exact_mini_mirror",
            "nexus_gitnexus_scope_hygiene",
            "nexus_gitnexus_scope_switch",
            "nexus_gitnexus_standalone_hud.v0.4.0",
        ]:
            self.assertNotIn(token, html)


if __name__ == "__main__":
    unittest.main()