import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronRoleSelector(unittest.TestCase):
    def test_selector_markup_exists_in_mode_selection(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("role-selector-panel", html)
        self.assertIn("empty-selector-panel", html)
        self.assertIn("mode-selection-button", html)
        self.assertIn("Mode Selection", html)
        self.assertIn("selector-knot", html)
        self.assertIn("role-select", html)
        self.assertIn("DEEP / Mistral", html)

    def test_left_rail_does_not_hold_active_selector(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        left = html.split("empty-selector-panel", 1)[1].split("</aside>", 1)[0]
        self.assertNotIn("selector-knot", left)
        self.assertNotIn("selector-hud-open", left)

    def test_selector_styles_exist(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("triangle -> Celtic knot", css)
        self.assertIn("knotCrystallize", css)
        self.assertIn("triangleToCrystal", css)
        self.assertIn("selector-switch", css)
        self.assertIn("mode-selection-button", css)

    def test_selector_js_is_ui_only(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("initRoleSelector", js)
        self.assertIn("bindModelSelectorHud", js)
        self.assertIn("toggleModelSelectorHud", js)
        self.assertIn("Selector changes UI planning context only", js)
        self.assertIn("DEEP -> Mistral", js)
        self.assertNotIn("exec(", js)
        self.assertNotIn("child_process", js)


if __name__ == "__main__":
    unittest.main()
