import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "electron" / "renderer" / "index.html"
CSS_PATH = REPO_ROOT / "electron" / "renderer" / "nexus_ui_center_chat_repair.v0.1.6l.css"
DOC_PATH = REPO_ROOT / "docs" / "runtime" / "NEXUS_UI_BALANCED_CHAT_LAYOUT.md"

class TestUiBalancedChatLayout(unittest.TestCase):
    def test_index_wires_l_repair_and_removes_old_experiments(self):
        text = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("nexus_ui_center_chat_repair.v0.1.6l.css", text)
        self.assertNotIn("nexus_ui_layout_balance_patch.v0.1.6.js", text)
        self.assertNotIn("nexus_ui_center_chat_close.v0.1.6j.js", text)
        self.assertNotIn("nexus_ui_center_chat_close.v0.1.6k.css", text)

    def test_css_targets_real_renderer_classes_without_chat_rewrite(self):
        text = CSS_PATH.read_text(encoding="utf-8")
        self.assertIn(".main-grid", text)
        self.assertIn(".left-stack > .lane-context", text)
        self.assertIn(".left-stack > .empty-selector-panel", text)
        self.assertIn(".console-panel.nex-chat-panel", text)
        self.assertIn(".right-stack", text)
        self.assertIn("--nexus-ui-l-side", text)
        self.assertIn("--nexus-ui-l-spacer", text)
        self.assertNotIn("grid-template-columns: 54px 88px", text)

    def test_doc_records_repair_intent(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("repair v0.1.6l", text)
        self.assertIn("full-window", text)
        self.assertIn("one intentional empty spacer", text)
        self.assertIn("equal side rails", text)

if __name__ == "__main__":
    unittest.main()
