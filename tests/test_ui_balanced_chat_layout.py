import json
import unittest
from pathlib import Path


SKIP = {".git", "node_modules", "dist", "build", ".next", "out", "__pycache__", ".venv", "venv"}


def iter_patch_files():
    for path in Path(".").rglob("nexus_ui_layout_balance_patch.v0.1.6.js"):
        if any(part in SKIP for part in path.parts):
            continue
        yield path


class TestUiBalancedChatLayout(unittest.TestCase):
    def test_readme_mentions_balanced_chat_rail_without_bloat(self):
        text = Path("README.md").read_text(encoding="utf-8-sig")
        self.assertLess(len(text.splitlines()), 220)
        self.assertIn("balanced chat rail", text)

    def test_manifest_records_ui_layout_patch(self):
        path = Path("state/ui/nexus_ui_balanced_chat_layout.v0.1.6.json")
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "0.1.6")
        self.assertIn("lane context box", data["request"]["remove"])
        self.assertGreaterEqual(len(data["applied_targets"]), 1)

    def test_renderer_patch_exists_and_contains_required_controls(self):
        patches = list(iter_patch_files())
        self.assertGreaterEqual(len(patches), 1)
        text = "\n".join(path.read_text(encoding="utf-8-sig") for path in patches)
        self.assertIn("LANE CONTEXT", text)
        self.assertIn("nexus-left-blank-spacer", text)
        self.assertIn("--nexus-side-rail-width", text)
        self.assertIn("MutationObserver", text)

    def test_docs_capture_request_boundary(self):
        text = Path("docs/runtime/NEXUS_UI_BALANCED_CHAT_LAYOUT.md").read_text(encoding="utf-8-sig")
        self.assertIn("remove the Lane Context box", text)
        self.assertIn("empty left-side spacer", text)
        self.assertIn("UI layout patch only", text)

    def test_html_entrypoints_are_wired_to_renderer_patch(self):
        data = json.loads(Path("state/ui/nexus_ui_balanced_chat_layout.v0.1.6.json").read_text(encoding="utf-8-sig"))
        for target in data["applied_targets"]:
            html = Path(target["html"])
            script = Path(target["script"])
            self.assertTrue(html.exists(), str(html))
            self.assertTrue(script.exists(), str(script))
            text = html.read_text(encoding="utf-8-sig")
            self.assertIn('data-nexus-ui-layout="balanced-chat-v0.1.6"', text)
            self.assertIn(script.name, text)


if __name__ == "__main__":
    unittest.main()
