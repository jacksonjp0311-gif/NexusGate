import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestRhpNexusSurface(unittest.TestCase):
    def test_root_readme_trisection(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in ["PART I - Human README", "PART II - RHP Nexus README", "PART III - AI Agent README"]:
            self.assertIn(marker, text)

    def test_context_files_exist(self):
        for rel in [
            "docs/context/repository_context_index.json",
            "docs/context/rcc_nexus_index.json",
            "docs/context/validation_surface.md",
            "rcc/nexus/route_map.json",
        ]:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_failure_modes_exist(self):
        text = (ROOT / "docs/failure_modes/FAILURE_MODES.md").read_text(encoding="utf-8")
        self.assertIn("schema_missing", text)
        self.assertIn("authority_unverified", text)
        self.assertIn("compiler_failed", text)

    def test_scripts_call_compiler_directly(self):
        for rel in [
            "scripts/nexus_compile.ps1",
            "scripts/nexus_once.ps1",
            "scripts/nexus_dev_loop.ps1",
            "scripts/nexus_promote.ps1",
            "scripts/nexus_compile.sh",
            "scripts/nexus_once.sh",
            "scripts/nexus_dev_loop.sh",
            "scripts/nexus_promote.sh",
        ]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("nexus_gate.compiler", text, rel)


if __name__ == "__main__":
    unittest.main()
