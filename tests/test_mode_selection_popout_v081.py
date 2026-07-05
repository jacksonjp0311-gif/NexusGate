import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestModeSelectionPopoutV081(unittest.TestCase):
    def test_mode_selection_button_stays_in_right_panel(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("mode-selection-button", html)
        self.assertIn("Mode Selection", html)
        self.assertIn('id="model-selector-toggle"', html)
        self.assertIn('id="model-selector-hud"', html)

    def test_mode_selection_hud_is_fixed_popout_like_telemetry(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS v0.8.1E: Mode Selection HUD is a fixed pop-out like Telemetry.", css)
        self.assertIn(".model-selector-hud", css)
        self.assertIn("position: fixed !important", css)
        self.assertIn("right: 28px", css)
        self.assertIn("top: 128px", css)
        self.assertIn("backdrop-filter: blur(10px)", css)
        self.assertIn(".model-selector-hud[hidden]", css)
        self.assertIn("display: none !important", css)

    def test_mode_selection_button_wires_open_and_close(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("function bindModelSelectorHud()", js)
        self.assertIn('modelSelectorToggle?.addEventListener("click", () => toggleModelSelectorHud());', js)
        self.assertIn('modelSelectorClose?.addEventListener("click", () => toggleModelSelectorHud(false));', js)
        self.assertIn('modelSelectorHud.style.display = next ? "" : "none";', js)


if __name__ == "__main__":
    unittest.main()
