import json
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
NEURAL_README = REPO_ROOT / "neural_activity" / "README.md"
NEURAL_INDEX = REPO_ROOT / "neural_activity" / "index.html"
DOC = REPO_ROOT / "docs" / "runtime" / "NEXUS_NEURAL_ACTIVITY.md"
MANIFEST = REPO_ROOT / "state" / "neural_activity" / "neural_activity_manifest.v0.1.1.json"


class TestNeuralActivityV011(unittest.TestCase):
    def test_main_readme_mentions_neural_activity_without_breaking_compactness(self):
        text = README.read_text(encoding="utf-8-sig")
        self.assertIn("Neural Activity", text)
        self.assertLess(len(text.splitlines()), 220)

    def test_neural_readme_locks_aa_as_canonical(self):
        text = NEURAL_README.read_text(encoding="utf-8-sig")
        self.assertIn("Canonical status: v0.1.1 visual organ", text)
        self.assertIn("AA is the canonical architecture", text)
        self.assertIn("surrogate previews = deprecated", text)

    def test_neural_index_has_embed_knobs(self):
        text = NEURAL_INDEX.read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS_NEURAL_ACTIVITY_V011_EMBED_KNOBS", text)
        self.assertIn("--nexus-neural-embed-scale", text)
        self.assertIn("embed", text)

    def test_runtime_doc_records_canonical_visual_organ(self):
        text = DOC.read_text(encoding="utf-8-sig")
        self.assertIn("v0.1.1 Canonical Visual Organ", text)
        self.assertIn("surrogate previews = deprecated", text)
        self.assertIn("HUD panel = live embedded Neural Cathedral preview", text)

    def test_manifest_records_boundary_and_deprecated_paths(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "v0.1.1")
        self.assertEqual(data["status"], "canonical_visual_organ")
        self.assertIn("AA live embedded", data["canonical_implementation"])
        self.assertIn("visual surface only", data["claim_boundary"])
        self.assertTrue(any("surrogate" in item for item in data["deprecated_paths"]))


if __name__ == "__main__":
    unittest.main()
