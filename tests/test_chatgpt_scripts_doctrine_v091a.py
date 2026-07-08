import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SCRIPT_DOC = ROOT / "chatgpt" / "scripts.md"


class TestChatGPTScriptsDoctrineV091A(unittest.TestCase):
    def test_script_doctrine_exists_and_is_required_before_coding(self):
        text = SCRIPT_DOC.read_text(encoding="utf-8-sig")
        for marker in [
            "Required Read Before Coding",
            "gates_are_certificates_do_not_backtrack_without_changed_inputs",
            "Every generated closer should print or write a compact state packet",
            "stage_policy",
            "human_authorized_only",
            "Do not stage unrelated runtime residue",
        ]:
            self.assertIn(marker, text)

    def test_root_readme_points_to_chatgpt_script_doctrine(self):
        text = README.read_text(encoding="utf-8-sig")
        self.assertIn("Before any future generated script changes this repo, read `chatgpt/scripts.md`.", text)
        self.assertIn("| ChatGPT scripting doctrine | `chatgpt/scripts.md` |", text)
        self.assertIn("Gates are certificates.", text)
        self.assertIn("Only heal the active wound.", text)
        self.assertLess(len(text.splitlines()), 220)

    def test_required_legacy_readme_markers_survive_professional_intro(self):
        text = README.read_text(encoding="utf-8-sig")
        for marker in [
            "Reflective Intelligence Layer for AI Systems",
            "local-first reflective intelligence layer for AI systems",
            "The portal is only the doorway",
            "observable, diagnosable, bounded",
            "v0.8.1 UI cleanup line",
            "GitHub / README / Docs",
            "Neural Activity v0.1.1",
            "Spiral Core Portal v0.1.2",
        ]:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
