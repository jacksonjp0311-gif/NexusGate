import json
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
DOC = REPO_ROOT / "docs" / "runtime" / "NEXUS_README_FRESHNESS_AUDIT.md"
MANIFEST = REPO_ROOT / "state" / "readme" / "readme_freshness_manifest.v0.1.2.json"


class TestReadmeFreshnessV012(unittest.TestCase):
    def test_readme_names_current_portal_and_neural_activity(self):
        text = README.read_text(encoding="utf-8-sig")
        self.assertIn("Spiral Core Desktop Portal", text)
        self.assertIn("blue/light-blue Spiral Core Portal", text)
        self.assertIn("Neural Activity v0.1.1", text)
        self.assertIn("Spiral Core Portal v0.1.2", text)
        self.assertIn("Neural Activity = visual organ.", text)

    def test_operator_surfaces_are_current(self):
        text = README.read_text(encoding="utf-8-sig")
        self.assertIn("| Spiral Core Desktop Portal |", text)
        self.assertIn("| Neural Activity | Canonical visual organ", text)
        self.assertNotIn("| Desktop Entry Portal | Human doorway into all local operator lanes. |", text)

    def test_documentation_map_includes_new_runtime_organs(self):
        text = README.read_text(encoding="utf-8-sig")
        neural = "| Neural Activity | `docs/runtime/NEXUS_NEURAL_ACTIVITY.md` |"
        spiral = "| Spiral Core Portal | `docs/runtime/NEXUS_SPIRAL_CORE_PORTAL.md` |"
        balanced = "| Balanced chat layout | `docs/runtime/NEXUS_UI_BALANCED_CHAT_LAYOUT.md` |"
        self.assertIn(neural, text)
        self.assertIn(spiral, text)
        self.assertIn(balanced, text)
        self.assertLess(text.index(balanced), text.index(neural))
        self.assertLess(text.index(neural), text.index(spiral))

    def test_strict_compact_root_readme_ceiling(self):
        text = README.read_text(encoding="utf-8-sig")
        self.assertLess(len(text.splitlines()), 220)

    def test_audit_doc_and_manifest_lock_boundary(self):
        doc = DOC.read_text(encoding="utf-8-sig")
        self.assertIn("Close E correction", doc)
        self.assertIn("strict root compactness gate", doc)
        self.assertIn("does not change runtime authority", doc)
        self.assertIn("Neural Activity", doc)
        self.assertIn("Spiral Core", doc)

        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "v0.1.2-close-e")
        self.assertTrue(data["no_authority_change"])
        self.assertTrue(data["no_execution_change"])
        self.assertIn("Strict compactness", data["updated_topics"])
        self.assertLess(data["actual_line_count"], data["strict_line_ceiling_exclusive"])


if __name__ == "__main__":
    unittest.main()
