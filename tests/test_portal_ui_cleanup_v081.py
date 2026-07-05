import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPortalUiCleanupV081(unittest.TestCase):
    def test_left_rail_reserved_box_is_empty(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("empty-selector-panel", index)
        empty_section = index.split("empty-selector-panel", 1)[1].split("</section>", 1)[0]
        self.assertNotIn("<button", empty_section)
        self.assertNotIn("<h2", empty_section)

    def test_mode_selection_still_available_under_system_monitor(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("system-monitor-station", index)
        self.assertIn("model-selector-toggle", index)
        self.assertIn("mode-selection-button", index)
        self.assertIn("Mode Selection", index)
        self.assertIn("model-selector-hud", index)

    def test_telemetry_close_contract(self):
        index = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        styles = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn('id="telemetry-close"', index)
        self.assertIn('toggleTelemetryHud(false)', renderer)
        self.assertIn(".telemetry-hud[hidden]", styles)
        self.assertIn("display: none !important", styles)


if __name__ == "__main__":
    unittest.main()
