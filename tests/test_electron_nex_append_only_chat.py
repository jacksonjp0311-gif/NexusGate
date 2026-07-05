import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronNexAppendOnlyChat(unittest.TestCase):
    def test_nex_response_is_not_mirrored_into_pinned_output(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn('appendChat("ai", visible', renderer)
        self.assertIn("append-only", renderer)
        self.assertNotIn('writeOutput(visible, { preTranslated: true });', renderer)
        self.assertNotIn('writeOutput(message, { preTranslated: true });', renderer)

    def test_stop_button_enabled_only_while_processing(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("stopButton.disabled = !active", renderer)
        self.assertIn("sendButton.disabled = active", renderer)

    def test_chat_css_is_scroll_bound(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS v0.6.9: append-only chat response stream", css)
        self.assertIn("scroll-behavior: smooth", css)
        self.assertIn("max-height: 210px", css)
        self.assertIn("#nex-ai-card .message-body pre", css)

    def test_doc_declares_append_only_contract(self):
        doc = (ROOT / "docs" / "ui" / "NEX_APPEND_ONLY_CHAT.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.6.9", doc)
        self.assertIn("responses now appear once", doc)
        self.assertIn("does not mirror", doc)


if __name__ == "__main__":
    unittest.main()
