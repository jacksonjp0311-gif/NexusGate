import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestRepoNativeLearning(unittest.TestCase):
    def test_repo_native_learning_doctrine_and_index(self):
        text = (ROOT / "docs/intelligence/REPO_NATIVE_LEARNING.md").read_text(encoding="utf-8")
        self.assertIn("not mutation of model weights", text)
        for card in ["SourceCard", "ConceptCard", "ClaimCard", "EquationCard", "SimulationCard", "CodePatternCard", "OrchestrationCard"]:
            self.assertIn(card, text)
        data = json.loads((ROOT / "state/repo_native_learning_index.v0.4.0.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.4.0")
        self.assertIn(".\\scripts\\nexus.ps1 domain", data["required_gates"])
        self.assertIn("not model-weight learning", data["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
