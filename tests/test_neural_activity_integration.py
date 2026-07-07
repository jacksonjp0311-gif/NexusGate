import json
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
NEURAL_INDEX = REPO_ROOT / "neural_activity" / "index.html"
ELECTRON_INDEX = REPO_ROOT / "electron" / "renderer" / "index.html"
PANEL_CSS = REPO_ROOT / "electron" / "renderer" / "nexus_neural_activity_panel.v0.1.0aa.css"
BRIDGE_JS = REPO_ROOT / "electron" / "renderer" / "nexus_neural_activity_bridge.v0.1.0aa.js"
MANIFEST = REPO_ROOT / "state" / "neural_activity" / "neural_activity_manifest.v0.1.0.json"


class TestNeuralActivityIntegration(unittest.TestCase):
    def test_static_reserved_box_remains_empty_for_portal_cleanup_contract(self):
        text = ELECTRON_INDEX.read_text(encoding="utf-8-sig")
        self.assertIn("empty-selector-panel", text)
        empty_section = text.split("empty-selector-panel", 1)[1].split("</section>", 1)[0]
        self.assertNotIn("<button", empty_section)
        self.assertNotIn("<h2", empty_section)
        self.assertNotIn("iframe", empty_section)
        self.assertNotIn("canvas", empty_section)
        self.assertNotIn("svg", empty_section)

    def test_cache_busted_aa_assets_are_wired(self):
        text = ELECTRON_INDEX.read_text(encoding="utf-8-sig")
        self.assertIn("nexus_neural_activity_panel.v0.1.0aa.css", text)
        self.assertIn("nexus_neural_activity_bridge.v0.1.0aa.js", text)
        self.assertNotIn("nexus_neural_activity_panel.v0.1.0z.css", text)
        self.assertNotIn("nexus_neural_activity_bridge.v0.1.0z.js", text)

    def test_runtime_bridge_uses_live_iframe_embed(self):
        js = BRIDGE_JS.read_text(encoding="utf-8-sig")
        self.assertIn('VERSION = "close-aa"', js)
        self.assertIn("neural-activity-live-frame", js)
        self.assertIn("document.createElement(\"iframe\")", js)
        self.assertIn("embed=1", js)
        self.assertIn("preview=1", js)
        self.assertIn("../../neural_activity/index.html", js)
        self.assertIn("setLight(light, true)", js)
        self.assertNotIn("buildDomPreview", js)
        self.assertNotIn("na-z-soma", js)
        self.assertNotIn("createElement(\"canvas\")", js)

    def test_neural_activity_has_embed_mode(self):
        text = NEURAL_INDEX.read_text(encoding="utf-8-sig")
        self.assertIn("nexus-neural-embed-aa-bootstrap", text)
        self.assertIn("nexus-neural-embed-aa-style", text)
        self.assertIn("nexus-neural-embed-aa", text)
        self.assertIn("Neural Cathedral", text)
        self.assertIn("three", text)

    def test_panel_css_declares_live_frame(self):
        css = PANEL_CSS.read_text(encoding="utf-8-sig")
        self.assertIn('data-neural-activity-mounted="close-aa"', css)
        self.assertIn(".neural-activity-live-frame", css)
        self.assertIn("inset: 0", css)
        self.assertIn("height: 100%", css)

    def test_manifest_records_boundary(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertIn("visual surface only", data["claim_boundary"])
        self.assertIn("close-aa", data["version"])


if __name__ == "__main__":
    unittest.main()
