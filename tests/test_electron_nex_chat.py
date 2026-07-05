import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronNexChat(unittest.TestCase):
    def test_chat_markup_is_primary(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("nex-chat-panel", html)
        self.assertIn("NEX AI Output", html)
        self.assertIn("chat-viewport", html)
        self.assertIn("nex-avatar", html)
        self.assertIn("operator-command", html)

    def test_chat_styles_define_buffer_and_processing(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("electric-chain", css)
        self.assertIn("iceBluePulse", css)
        self.assertIn("nexProcessingPulse", css)
        self.assertIn("cyberpunk orange", css)

    def test_chat_renderer_uses_bounded_nex_bridge(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("sendNexMessage", js)
        self.assertIn("window.nexus.askNex", js)
        self.assertIn("Shift+Enter", js)
        self.assertIn("recommendation-only", js)

    def test_preload_exposes_ask_nex(self):
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8")
        self.assertIn("askNex", preload)

    def test_main_bridge_is_bounded(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8")
        self.assertIn("nexus:askNex", main)
        self.assertIn("NEX_CHAT_ROLES", main)
        self.assertIn("shell: false", main)
        self.assertNotIn("exec(", main)
        self.assertNotIn("execFile(", main)


if __name__ == "__main__":
    unittest.main()

