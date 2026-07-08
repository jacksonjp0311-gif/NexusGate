from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "electron" / "renderer" / "index.html"
RENDERER = ROOT / "electron" / "renderer"


def active_conversation_bridge_scripts() -> list[str]:
    html = INDEX.read_text(encoding="utf-8", errors="ignore")
    return re.findall(
        r'<script\s+[^>]*src="\./(nexus_conversation_output_bridge\.v0\.2\.1[a-z]\.js)"[^>]*>\s*</script>',
        html,
        flags=re.IGNORECASE,
    )


class TestNexusConversationOutputBridgeV021A(unittest.TestCase):
    def test_bridge_lineage_collapses_to_v021f(self):
        scripts = active_conversation_bridge_scripts()
        self.assertEqual(scripts, ["nexus_conversation_output_bridge.v0.2.1f.js"])

    def test_legacy_v021a_is_not_active_script(self):
        scripts = active_conversation_bridge_scripts()
        self.assertNotIn("nexus_conversation_output_bridge.v0.2.1a.js", scripts)

    def test_v021f_asset_exists(self):
        self.assertTrue((RENDERER / "nexus_conversation_output_bridge.v0.2.1f.js").exists())


if __name__ == "__main__":
    unittest.main()