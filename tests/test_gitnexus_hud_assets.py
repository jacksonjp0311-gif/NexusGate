from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"


class TestGitNexusHudAssets(unittest.TestCase):
    def test_scope_hygiene_overlay_is_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_scope_hygiene.v0.3.8.css", html)
        self.assertIn("nexus_gitnexus_scope_hygiene.v0.3.8.js", html)

    def test_active_bridge_is_v021f_only(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        active = sorted(set(re.findall(r"nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js", html)))
        self.assertEqual(active, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_scope_hygiene_denies_generated_artifacts(self):
        js = (ROOT / "electron" / "renderer" / "nexus_gitnexus_scope_hygiene.v0.3.8.js").read_text(
            encoding="utf-8", errors="ignore"
        )
        for token in [
            "reports",
            "state",
            "ledger",
            "compact_compile_logs",
            "Tesseract Neural Network",
            "nexus_gitnexus_",
            "nexus_conversation_output_bridge",
            "CORE SCOPE",
        ]:
            self.assertIn(token, js)

    def test_single_owner_assets_are_still_linked(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_core_hud.v0.3.7.js", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.css", html)
        self.assertIn("nexus_gitnexus_geometric_mini.v0.3.7.js", html)

    def test_no_gitnexus_in_metrics_body_tail(self):
        html = INDEX.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<!-- NEXUS_METRICS_HUD_V010_SCRIPT_END -->.*?</body>", html, re.S)
        if match:
            self.assertNotIn("nexus_gitnexus_core_hud", match.group(0))
            self.assertNotIn("nexus_gitnexus_geometric_mini", match.group(0))
            self.assertNotIn("nexus_gitnexus_scope_hygiene", match.group(0))


if __name__ == "__main__":
    unittest.main()