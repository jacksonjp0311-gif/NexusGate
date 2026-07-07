from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "electron" / "renderer" / "index.html"
BRIDGE = ROOT / "electron" / "renderer" / "nexus_mode_role_truth_bridge.v0.2.0zw.js"
MANIFEST = ROOT / "state" / "nexus_mode_role_manifest.v0.2.0zw.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


class TestNexusModeRoleTruthBridgeV020ZW(unittest.TestCase):
    def test_bridge_is_linked(self):
        html = read(HTML)
        self.assertIn("nexus_mode_role_truth_bridge.v0.2.0zw.js", html)

    def test_manifest_maps_fast_balanced_to_phi4(self):
        data = json.loads(read(MANIFEST))
        self.assertEqual(data["roles"]["FAST"]["backend"], "tnn-phi4-mini:latest")
        self.assertEqual(data["roles"]["BALANCED"]["backend"], "tnn-phi4-mini:latest")
        self.assertTrue(data["roles"]["FAST"]["available"])
        self.assertTrue(data["roles"]["BALANCED"]["available"])

    def test_tnn_maps_to_phi4_hot_brain(self):
        data = json.loads(read(MANIFEST))
        self.assertEqual(data["roles"]["TNN"]["brain"], "Tesseract Neural Network/phi4-mini-hot-brain")
        blob = read(BRIDGE) + read(MANIFEST)
        self.assertIn("phi4-mini-hot-brain", blob)
        retired_brain = "mistral-" + "chat-brain"
        self.assertNotIn(retired_brain, blob)

    def test_phi4_truth_tokens_are_present_and_retired_tokens_absent(self):
        blob = read(BRIDGE) + read(MANIFEST)
        self.assertIn("Phi-4-mini", blob)
        self.assertIn("tnn-phi4-mini:latest", blob)
        retired_display = "Phi" + "-3"
        retired_lower = "phi" + "3"
        self.assertNotIn(retired_display, blob)
        self.assertNotIn(retired_lower, blob)

    def test_bridge_patches_stale_summary_text(self):
        js = read(BRIDGE)
        self.assertIn("BALANCED: tnn-phi4-mini:latest / available=true", js)
        self.assertIn("FAST: tnn-phi4-mini:latest / available=true", js)
        self.assertIn("nexusSelectedRoleTruth", js)

    def test_manifest_has_no_bom(self):
        raw = MANIFEST.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()