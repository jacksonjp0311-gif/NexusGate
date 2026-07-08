from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_scope_switch_is_linked_and_hard_lock_removed(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_scope_switch.v0.3.9.css", html)
        self.assertIn("nexus_gitnexus_scope_switch.v0.3.9.js", html)
        self.assertNotIn("nexus_gitnexus_scope_hygiene.v0.3.8", html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_scope_switch_defaults_to_all_not_locked(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_scope_switch.v0.3.9.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        css = (ROOT / "electron" / "renderer" / "nexus_gitnexus_scope_switch.v0.3.9.css").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn('mode: "all"', js)
        self.assertIn("gitnexusScopeAll", js)
        self.assertIn("gitnexusScopeCore", js)
        self.assertIn("removeOldLockoutState", js)
        self.assertIn('data-gitnexus-scope-mode="core"', css)
        self.assertIn('data-gitnexus-scope-mode="all"', css)

    def test_single_owner_assets_remain_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.js", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.js", html)


if __name__ == "__main__":
    unittest.main()