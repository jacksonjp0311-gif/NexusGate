import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPortalRehydrateUiV080(unittest.TestCase):
    def test_launcher_has_cyber_portal_geometry(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Write-Portal", script)
        self.assertIn("cyber ice-blue gateway", script)
        self.assertIn("The gate does not give intelligence authority.", script)
        self.assertIn("[8] Failure Modes / Doctor", script)
        self.assertIn("portal -> surface -> evidence -> gate -> durable commit", script)

    def test_left_selector_box_is_empty_and_selector_lives_in_mode_selection(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("empty-selector-panel", index)
        self.assertIn('data-empty-left-rail="true"', index)
        self.assertNotIn("Relay Glyph", index)
        self.assertNotIn("selector-hud-open", index)
        self.assertIn("model-selector-station", index)
        self.assertIn("Mode Selection", index)
        self.assertIn("model-selector-hud", index)

    def test_renderer_controls_model_selector_hud_without_left_glyph(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("const modelSelectorHud", renderer)
        self.assertIn("function toggleModelSelectorHud", renderer)
        self.assertIn("selectorSwitch?.addEventListener", renderer)
        self.assertIn("modelSelectorToggle", renderer)
        self.assertIn("selectorHudStatus", renderer)
        self.assertEqual(renderer.count("if (selectorHudStatus) selectorHudStatus.textContent = setting.label;"), 1)

    def test_telemetry_close_has_hidden_css_and_style_fallback(self):
        styles = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn(".telemetry-hud[hidden]", styles)
        self.assertIn("display: none !important", styles)
        self.assertIn('telemetryHud.style.display = next ? "" : "none";', renderer)

    def test_styles_define_yellow_black_selector_hud(self):
        styles = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn(".model-selector-hud", styles)
        self.assertIn(".model-selector-button", styles)
        self.assertIn("#facc15", styles)

    def test_readme_and_versioning_rehydrated(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        version_doc = (ROOT / "docs" / "versioning" / "NEXUS_VERSIONING_REHYDRATION.md").read_text(encoding="utf-8-sig")
        self.assertIn("Reflective Intelligence Layer for AI Systems", readme)
        self.assertIn("## NEXUS Connective Point", readme)
        self.assertIn("v0.8.1 UI cleanup line", readme)
        self.assertIn("Portal = gateway", version_doc)
        self.assertIn("Nexus Gate = reflective intelligence layer for AI systems.", version_doc)

    def test_package_description_mentions_reflective_intelligence(self):
        package = json.loads((ROOT / "electron" / "package.json").read_text(encoding="utf-8"))
        self.assertIn("Reflective intelligence HUD", package["description"])

    def test_package_json_has_no_utf8_bom(self):
        raw = (ROOT / "electron" / "package.json").read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
