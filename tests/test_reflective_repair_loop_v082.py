import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestReflectiveRepairLoopV082(unittest.TestCase):
    def test_reflective_repair_script_uses_nexus_deep_and_human_gate(self):
        script = (ROOT / "scripts" / "nexus_reflective_repair.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS-REFLECT", script)
        self.assertIn(".\\scripts\\nexus.ps1", script)
        self.assertIn('"deep"', script)
        self.assertIn("-CallModel", script)
        self.assertIn("recommendation only", script)
        self.assertIn("Read-Host", script)
        self.assertIn("[y/N]", script)
        self.assertIn("Human approved", script)
        self.assertIn("Human declined", script)

    def test_algorithm_doc_describes_reflective_repair(self):
        doc = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8")
        self.assertIn("Reflective Repair Algorithm", doc)
        self.assertIn("NEXUS DEEP/Mistral recommendation", doc)
        self.assertIn("Y/N human gate", doc)


if __name__ == "__main__":
    unittest.main()
