import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronRoleSelector(unittest.TestCase):
    def test_selector_markup_exists(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("role-selector-panel", html)
        self.assertIn("selector-knot", html)
        self.assertIn("role-select", html)
        self.assertIn("DEEP / Mistral", html)

    def test_selector_styles_exist(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("triangle -> Celtic knot", css)
        self.assertIn("knotCrystallize", css)
        self.assertIn("triangleToCrystal", css)
        self.assertIn("selector-switch", css)

    def test_selector_js_is_ui_only(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("initRoleSelector", js)
        self.assertIn("Selector changes UI planning context only", js)
        self.assertIn("DEEP -> Mistral", js)
        self.assertNotIn("exec(", js)
        self.assertNotIn("child_process", js)


if __name__ == "__main__":
    unittest.main()
