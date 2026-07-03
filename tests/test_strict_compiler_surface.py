import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestStrictCompilerSurface(unittest.TestCase):
    def test_strict_compiler_scripts_exist(self):
        self.assertTrue((ROOT / "scripts" / "nexus_strict_compile.ps1").exists())
        self.assertTrue((ROOT / "scripts" / "nexus_strict_compile.sh").exists())

    def test_cold_evidence_docs_exist(self):
        cold = (ROOT / "docs" / "evidence" / "COLD_EVIDENCE_ENGINE.md").read_text(encoding="utf-8")
        wound = (ROOT / "docs" / "failure_modes" / "WOUND_ROUTING.md").read_text(encoding="utf-8")
        for marker in ["ShadowReport", "ShadowFailure", "ShadowWound", "WoundRoute", "ReplayCertificate", "DemotionDecision"]:
            self.assertIn(marker, cold + wound)

    def test_compact_command_has_strict_mode(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn("strict", ps)
        self.assertIn("strict", sh)


if __name__ == "__main__":
    unittest.main()
