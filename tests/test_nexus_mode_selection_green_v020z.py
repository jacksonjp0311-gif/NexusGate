from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "electron" / "renderer" / "index.html"
CSS = ROOT / "electron" / "renderer" / "nexus_mode_selection_green.v0.2.0z.css"
JS = ROOT / "electron" / "renderer" / "nexus_mode_selection_green.v0.2.0z.js"


class TestNexusModeSelectionGreenV020Z(unittest.TestCase):
    def test_assets_are_linked(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("nexus_mode_selection_green.v0.2.0z.css", html)
        self.assertIn("nexus_mode_selection_green.v0.2.0z.js", html)

    def test_phi4_labels_replace_phi3_in_selector_assets(self):
        js = JS.read_text(encoding="utf-8")
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("FAST / Phi-4-mini", js)
        self.assertIn("BALANCED / Phi-4-mini", js)
        self.assertIn("FAST / Phi-4-mini", html)
        self.assertIn("BALANCED / Phi-4-mini", html)
        self.assertNotIn("FAST / Phi-3", js)
        self.assertNotIn("BALANCED / Phi-3", js)
        self.assertNotIn("FAST / Phi-3", html)
        self.assertNotIn("BALANCED / Phi-3", html)

    def test_green_theme_targets_mode_and_system_monitor(self):
        css = CSS.read_text(encoding="utf-8")
        for marker in [
            "--nexus-mode-green",
            ".model-selector-hud",
            "#role-select",
            ".system-monitor-station",
            ".telemetry-popout-button",
            ".model-selector-button.mode-selection-button",
            ".nexus-mode-green-option",
        ]:
            self.assertIn(marker, css)

    def test_renderer_keeps_compatibility_markers(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("AI Handoff Package", html)
        self.assertIn("Process Lanes", html)
        self.assertIn("Feedback Summary", html)


if __name__ == "__main__":
    unittest.main()
