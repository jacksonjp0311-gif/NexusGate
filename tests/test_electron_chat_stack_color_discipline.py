import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronChatStackColorDiscipline(unittest.TestCase):
    def test_chat_stack_override_is_present(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS v0.7.2: chat stack discipline", css)
        self.assertIn("display: flex !important", css)
        self.assertIn("flex-direction: column !important", css)
        self.assertIn("flex: 0 0 auto !important", css)
        self.assertIn("isolation: isolate !important", css)

    def test_human_chat_is_iceborg_blue(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("HUMAN = Iceborg blue", css)
        self.assertIn(".human-message .message-body", css)
        self.assertIn("#dbeafe", css)
        self.assertIn("rgba(96, 165, 250", css)

    def test_nex_chat_is_cyberpunk_green(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("NEX = vibe-coder cyberpunk green", css)
        self.assertIn(".ai-message .message-body", css)
        self.assertIn("#dcfce7", css)
        self.assertIn("rgba(34, 197, 94", css)

    def test_system_error_red_overrides_normal_nex(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn(".chat-message.system-error-message .message-body", css)
        self.assertIn("#fee2e2", css)

    def test_doc_declares_visual_contract(self):
        doc = (ROOT / "docs" / "ui" / "NEX_CHAT_STACK_COLOR_DISCIPLINE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Version: v0.7.2", doc)
        self.assertIn("Human chat is Iceborg blue", doc)
        self.assertIn("NEX chat is vibe-coder cyberpunk green", doc)


if __name__ == "__main__":
    unittest.main()
