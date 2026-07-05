import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronSystemMonitorErrorHud(unittest.TestCase):
    def test_telemetry_hud_starts_closed_and_error_hud_exists(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn('id="telemetry-hud" hidden', html)
        self.assertIn('id="system-error-hud" hidden', html)
        self.assertIn('id="system-error-report"', html)
        self.assertIn("System Compiled Error", html)

    def test_renderer_builds_system_error_report_without_ai(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("function buildSystemErrorReport", renderer)
        self.assertIn("Compiled by: NEXUS renderer/system bridge", renderer)
        self.assertIn("function showSystemErrorHud", renderer)
        self.assertIn("function clearSystemErrorHud", renderer)
        self.assertIn("system-error-active", renderer)
        self.assertIn("system-error-message", renderer)

    def test_renderer_realtime_monitor_and_append_only_chat(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("function startTelemetryLoop", renderer)
        self.assertIn("setInterval(refreshTelemetry, 1000)", renderer)
        self.assertIn("toggleTelemetryHud(false)", renderer)
        self.assertIn("stopButton.disabled = !active", renderer)
        self.assertIn('stage: "nex_model_bridge"', renderer)
        self.assertIn('stage: "nex_chat_exception"', renderer)
        self.assertNotIn('writeOutput(visible, { preTranslated: true });', renderer)
        self.assertNotIn('writeOutput(message, { preTranslated: true });', renderer)

    def test_css_has_red_error_hud_and_bigger_monitor(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS v0.7.0: real-time monitor", css)
        self.assertIn(".system-error-hud", css)
        self.assertIn("body.system-error-active .nex-chat-panel", css)
        self.assertIn("font: 900 14px Consolas", css)
        self.assertIn("z-index: 12", css)

    def test_doc_declares_system_compiled_not_model_generated(self):
        doc = (ROOT / "docs" / "ui" / "NEX_SYSTEM_MONITOR_ERROR_HUD.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.7.0", doc)
        self.assertIn("not model-generated AI text", doc)
        self.assertIn("refreshes once per second", doc)


if __name__ == "__main__":
    unittest.main()
